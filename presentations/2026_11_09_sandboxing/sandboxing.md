# Harnessing the Harness: Keeping your AI Agents on a short leash

LLM agents are incredibly powerful tools. But do you really want to give Sam Altman write access to your entire file system?

In this hands-on tutorial, I'll show you how to run AI agents like OpenCode and Claude Code in Docker sandboxes, restricting their file system access to your project instead of giving them free rein over your machine. Bring your
laptop if you want to follow along and set up your own sandbox!

In this tutorial we are going to use Docker Sandboxes: `sbx`. We focus here on the LMU Physik cluster, but most of the elements discussed here should work on any computer with only slight modifications.

## Docker

Docker Sandboxes `sbx` are based on -- you guessed it -- Docker. The LMU Physik cluster uses podman, aliased as `docker`. Most of the commands are identical to Docker and it is not needed to install Docker itself.

To install Docker on your machine, consult the [Docker documentation](https://docs.docker.com/).

## Docker Sandboxes

In the next step we need to install `sbx`.

### Personal Computer

On your personal machine you can run the following command, which also installs the Docker engine in one go:

```bash
curl -fsSL https://get.docker.com | sudo SBX=1 sh
```

If you already have Docker installed you can install `sbx` only with the following command:

```bash
curl -fsSL https://get.docker.com | sudo REPO_ONLY=1 sh
sudo apt install docker-sbx
```

### LMU Physik cluster

On the Physik cluster, the situation is more complex. On the one hand we do not have `sudo` rights to install `sbx` with the above command. On the other hand we need to use a wrapper which stores temporary files on `$SCRATCH` since `$HOME`
will typically be too small.

Instead of installing `sbx` the usual way, we are downloading the latest pre-compiled binary release from GitHub:

```bash
mkdir -p ~/.local/opt/sbx && cd ~/.local/opt/sbx
URL=$(curl -fsSL https://api.github.com/repos/docker/sbx-releases/releases/latest \
      | grep -o '"browser_download_url": *"[^"]*linux[^"]*amd64[^"]*\.tar\.gz"' \
      | cut -d'"' -f4)
echo "$URL"
curl -fsSL "$URL" -o sbx.tar.gz && tar xzf sbx.tar.gz && rm sbx.tar.gz
```

These commands will create the directory `~/.local/opt/sbx` in your `$HOME` directory, will download the latest release suitable for the Physik cluster hardware, and will unpack the compressed archive.

The `sbx` binary will now be sitting at `~/.local/opt/sbx/docker-sbx/sbx`.

But we are not calling this binary directly. Instead we create the file `~/.local/bin/sbx`

```bash
#!/usr/bin/env bash

base=$SCRATCH/.local/sbx
mkdir -p "$base"/{state,data,cache}
export XDG_STATE_HOME=$base/state XDG_DATA_HOME=$base/data XDG_CACHE_HOME=$base/cache
exec "$HOME/.local/opt/sbx/docker-sbx/sbx" "$@"
```

Don't forget to make the wrapper executable:

```bash
chmod +x ~/.local/bin/sbx
```

This file is a wrapper for `sbx` which is instead storing all temporary files in `$SCRATCH/.local/sbx` instead of our `$HOME` directory. `sbx` is essentially running a separate operating system in a virtual machine. Therefore, these temporary files can easily be several gigabytes large and potentially larger than the available quota on `$HOME`.

Make sure that the wrapper is in your `$PATH` if it is not already:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### First use

Usage of `sbx` requires a Docker account. When first using `sbx` you need to log in:

```bash
sbx login
```

Follow the steps and log in. If you are asked for your choice of network policy, choose option 2 (balanced).

## Docker templates

`sbx` could be used without any custom templates. But it may be a good idea to set up the virtual machines according to your preferences. A `Dockerfile` template will be provided. The syntax should be mostly self-explanatory and can be adjusted to your needs, e.g. for which agent you are building the sandbox, Opencode or Claude Code.

Once your `Dockerfile` is ready you need to build the image. The following steps can take several minutes. The option `--format docker` is only needed when Podman is used instead of Docker, as is the case on the LMU Physik cluster.

```bash
docker build -f Dockerfile --format docker --no-cache --tag agent .
docker image save agent -o agent.tar
sbx template load agent.tar
```

Afterwards the `.tar` file can be deleted:

```bash
rm agent.tar
```

## Secrets

We could already run the sandbox. But to use the `qwen3.8-27B` model on the LMU Physik cluster we need to pass our access token into our sandbox. We do not want to store the token directly in the sandbox, so our LLM agent will never have access to it.

To get your own personal access token visit the following site -- LMU account required:

[https://collab.dvb.bayern/spaces/LMULMPHGST/pages/224496314/Inference+Service+Copilot](https://collab.dvb.bayern/spaces/LMULMPHGST/pages/224496314/Inference+Service+Copilot)

To pass the token into the sandbox we need to register a secret with `sbx`. To do so run the following command:

```bash
sbx secret set-custom \
	--host inference.server.physik.uni-muenchen.de \
	--env LMUPHYSIK_ACCESS_TOKEN \
	--value <your_token>
```

What this command does is it will set an environment variable `$LMUPHYSIK_ACCESS_TOKEN` inside the sandbox which has some nonsense assigned to it, i.e. a placeholder for example `sbx-cs-JK9Jq9vznCR3e0On`. The LLM agent inside the sandbox will only see this placeholder, not your real token. Whenever this placeholder is sent to the URL specified in `--host` -- and only then -- the sandbox will replace the placeholder with your actual key.

In the `Dockerfile` earlier we also specified a configuration file for Opencode which is using the environment variable `$LMUPHYSIK_ACCESS_TOKEN`. This will only work if we use this name in the `sbx secret set-custom` command.

If you have API keys to other providers you can register them in a similar way. For the most common providers `sbx` has already pre-defined commands:

```bash
sbx secret set openai
sbx secret set anthropic
```

## Network Policies

We earlier set the network policies to balanced. This will allow the sandbox to access the most common websites needed for agentic programming. However, we will need to allow more websites to be accessed by the sandbox. For example the LMU Physik server. To do so we need to run the command:

```bash
sbx policy allow network inference.server.physik.uni-muenchen.de
```

You can run this command for other websites you need your sandbox to have access to.

## Starting up

Now we can finally start up our sandbox with the command

```bash
sbx run --pull never -t <template-name> --name <sandbox-name> opencode .
```

This will start a sandbox named `<sandbox-name>` using the template `<template-name>` and start Opencode in it. The current directory `.` will be the root of the project directory. The sandbox can not access anything outside of it. `--pull never` will make sure that no image will be pulled from the Docker repository if our template is not found.

Once the sandbox has been started up we can also just use the `sbx` dashboard to manage it and return to our session.

## Logging in

We can log in to our running sandbox using this command

```bash
sbx exec -t <sandbox-name> zsh
```

This will run `zsh` in our sandbox. The `-t` flag will allocate a TTY to it. This will log us in to the sandbox as the user agent. Not root. To run a command as root we need to pass the `-u root` flag:

```bash
sbx exec -u root <sandbox-name> opencode upgrade
```

## Useful wrappers

The commands above are quite lengthy. We can add more wrappers into `~/.local/bin`. The first one is for starting up our template sandbox. Consider the file `~/.local/bin/sandbox`

```bash
#!/usr/bin/env bash

flavor=${1}
name=${2}

tname=$(sbx template ls --format json 2>/dev/null \
    | jq -r --arg f "$flavor" '.[] | select(.repository == $f
        or (.repository | endswith("/" + $f))) | .repository + ":" + .tag' \
    | head -n 1)
[ -n "$tname" ] || {
    printf 'sandbox: no template registered for "%s" (see `sbx template ls`); run `make images`\n' "$flavor" >&2
    exit 1
}

exec sbx run --pull never -t "$tname" --name "$name" "$flavor" . "$@"
```

Make the wrapper executable, as before:

```bash
chmod +x ~/.local/bin/sandbox
```

The `sandbox` wrapper takes two positional arguments `$flavor` and `$name`. It is then checking if a template for that flavor is registered with `sbx` and is loading that template in a new `sbx` session with the chosen name.

```bash
sandbox <opencode|claude> <sandbox-name>
```

Another useful wrapper is for the `sbx exec` command to run commands in the sandbox. Consider the file
`~/.local/bin/xsbx`:

```bash
#!/usr/bin/env bash

name=$1; shift
if [ "$#" -ge 2 ] && [ "$1" = root ]; then
  shift
  exec sbx exec -t -u root "$name" -- "$@"
fi
exec sbx exec -t "$name" -- "$@"
```

Make this wrapper executable as well:

```bash
chmod +x ~/.local/bin/xsbx
```

This wrapper is running the given command with the `-t` flag in the sandbox with the given name:

```bash
xsbx <sandbox-name> zsh
```

would run `zsh` in the sandbox `<sandbox-name>` as the user agent.

```bash
xsbx <sandbox-name> root opencode upgrade
```

would run the command `opencode upgrade` as root user in the sandbox with the name `<sandbox-name>`.

## Typical Workflow using Git

Usually you would use Git to manage your project. There are two ways of integrating Git and the Docker Sandbox into your workflow: direct mode and clone mode.

### Direct mode

Here your project is a Git repository and you start your sandbox in the root of your project. If you have configured your sandbox template with Git the agent now has access to your git repository, can make changes and commit them to the repository. These changes are then immediately visible outside the sandbox.

You could also tell the agent not to commit anything to the repository. Now you can always use `git diff` to review what the agent has changed in your project, approve it, and commit it manually.

### Clone mode

In clone mode you start your sandbox with the `--clone` option:

```bash
sbx run --pull never -t <sandbox-template> --name <sandbox-name> --clone <flavor> .
```

Or with the wrapper:

```bash
sandbox <flavor> <sandbox-name> --clone
```

In this case, the sandbox is a remote repository. The agent can commit changes and on the host you can fetch and pull them.

**Note:** This only works as long as the sandbox is running. Once the sandbox is stopped the remote repository vanishes.

## Setup helper

These were quite some steps to get your sandbox running. In this repository you can find Makefiles that allow you to set up the sandbox on the LMU Physik cluster in one go:

[https://gitlab.physik.lmu.de/Sebastian.Stammler/agentic-toolbox](https://gitlab.physik.lmu.de/Sebastian.Stammler/agentic-toolbox)

Simply run

```bash
make all
```

in the base directory of the repository. The process will take several minutes. And during the setup phase you will be asked to log in to Docker and to provide your API Token for the LMU Physik inference server.

**Note:** The LMU Physik GitLab server is currently only accessible from within the Münchner Wissenschaftsnetz MNW. Make sure to use a VPN if you are trying to access it from outside.
