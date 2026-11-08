FROM docker/sandbox-templates:opencode

# Make piped RUN commands fail if either side of the pipe fails.
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

USER root

#------------------------------------------------------------------------------
# Installing tools
#------------------------------------------------------------------------------

# Useful commands
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y \
    --no-install-recommends \
    ca-certificates \
    curl \
    git \
    git-lfs \
    zsh \
    ripgrep \
    fd-find \
    bat \
    jq \
    less \
    vim \
    unzip \
    zip \
    tree \
    file \
    procps \
    pkg-config \
    build-essential \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Update opencode
RUN npm uninstall -g opencode-ai || true && \
  npm install -g opencode-ai && \
  opencode upgrade --major && \
  opencode upgrade && \
  opencode --version

# Starship
RUN curl -fsSL https://starship.rs/install.sh | sh -s -- -y

# LaTeX
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y \
    --no-install-recommends \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-science \
    texlive-publishers \
    texlive-xetex \
    texlive-lang-german \
    latexmk \
    biber \
    nano \
    && rm -rf /var/lib/apt/lists/*

#------------------------------------------------------------------------------
# User agent
#------------------------------------------------------------------------------

# zsh as the agent user's default shell
RUN usermod -s /usr/bin/zsh agent

USER agent


# Environmental variables
ENV PATH="/home/agent/.local/bin:/home/agent/.pixi/bin:${PATH}"
ENV OPENCODE_ENABLE_EXA="1" \
    OPENCODE_EXPERIMENTAL_LSP_TOOL="true"

# Git configuration
RUN cat > "$HOME/.gitconfig" <<'EOF'
[user]
    name = Opencode
    email = opencode@sandbox
[alias]
    hist = log --pretty=format:'%C(yellow)[%ad]%C(reset) %C(green)[%h]%C(reset) | %s %C(bold red)(%an)%C(reset) %C(green)%d%C(reset)' --graph --date=short
[core]
    editor = nano
[init]
    defaultBranch = main
[pull]
    rebase = false
EOF

#------------------------------------------------------------------------------
# Installing tools
#------------------------------------------------------------------------------

# Pixi
RUN curl -fsSL https://pixi.sh/install.sh | bash

# Pixi settings
RUN mkdir -p "$HOME/.config/pixi"
RUN cat > "$HOME/.config/pixi/config.toml" <<'EOF'
[shell]
change-ps1 = false
EOF

# Python formatting
RUN pixi global install basedpyright \
    && pixi global install ruff

# fdfind and batcat
RUN mkdir -p "$HOME/.local/bin" \
    && ln -sf /usr/bin/fdfind "$HOME/.local/bin/fd" \
    && ln -sf /usr/bin/batcat "$HOME/.local/bin/bat"

# opencode.jsonc
RUN mkdir -p "$HOME/.config/opencode"
RUN cat > "$HOME/.config/opencode/opencode.jsonc" <<'EOF'
{
  "$schema": "https://opencode.ai/config.json",

  // Default: LMU Physik cluster
  "model": "lmuphysik/qwen3-coder",

  "provider": {
    "lmuphysik": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "LMU Physik",
      "options": {
        "baseURL": "https://inference.server.physik.uni-muenchen.de/v1",
        "apiKey": "{env:LMUPHYSIK_ACCESS_TOKEN}"
      },
      "models": {
        "qwen3-coder": {
          "name": "Qwen3.8-27B"
        }
      }
    }
  }
}
EOF


# Oh-My-Zsh (unattended + keep-zshrc: no prompts, no shell change, and
# .zshrc untouched — the block at the bottom appends the source lines)
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended --keep-zshrc

# zsh-autosuggestions, as an oh-my-zsh custom plugin (no prompts)
RUN git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions \
    "$HOME/.oh-my-zsh/custom/plugins/zsh-autosuggestions"

# Starship formatting
RUN mkdir -p "$HOME/.config"
RUN cat >> "$HOME/.config/starship.toml" <<'EOF'
"$schema" = 'https://starship.rs/config-schema.json'

format = """
[](color_purple)\
$os\
$username\
[](fg:color_purple bg:color_red)\
$directory\
[](fg:color_red bg:color_yellow)\
$git_branch\
$git_status\
[](fg:color_yellow bg:color_lightblue)\
$c\
$rust\
$golang\
$nodejs\
$php\
$java\
$kotlin\
$haskell\
$python\
[](fg:color_lightblue bg:color_darkblue)\
$docker_context\
$conda\
[ ](fg:color_darkblue)\
$line_break$character"""

palette = 'gruvbox_dark'
command_timeout = 3000

[palettes.gruvbox_dark]
color_fg0 = '#FFDDFF'
color_fg1 = '#FFEEEE'
color_fg2 = '#FFFFDD'
color_fg3 = '#222255'
color_fg4 = '#000033'
color_purple = '#9A348E'
color_red = '#DA627D'
color_yellow = '#FCA17D'
color_lightblue = '#86BBD8'
color_darkblue = '#33658A'

[os]
disabled = false
style = "fg:color_fg0 bg:color_purple"

[os.symbols]
Windows = "󰍲"
Ubuntu = "󰕈"
SUSE = ""
Raspbian = "󰐿"
Mint = "󰣭"
Macos = "󰀵"
Manjaro = ""
Linux = "󰌽"
Gentoo = "󰣨"
Fedora = "󰣛"
Alpine = ""
Amazon = ""
Android = ""
Arch = "󰣇"
Artix = "󰣇"
EndeavourOS = ""
CentOS = ""
Debian = "󰣚"
Redhat = "󱄛"
RedHatEnterprise = "󱄛"
Pop = ""

[username]
show_always = true
style_user = "fg:color_fg0 bg:color_purple"
style_root = "fg:color_fg0 bg:color_purple"
format = '[ $user ]($style)'

[directory]
style = "fg:color_fg1 bg:color_red"
format = "[ $path ]($style)"
truncation_length = 3
truncation_symbol = "…/"

[directory.substitutions]
"Documents" = "󰈙 "
"Downloads" = " "
"Music" = "󰝚 "
"Pictures" = " "
"Developer" = "󰲋 "

[git_branch]
symbol = ""
style = "bg:color_yellow"
format = '[[ $symbol $branch ](fg:color_fg2 bg:color_yellow)]($style)'

[git_status]
style = "bg:color_yellow"
format = '[[($all_status$ahead_behind )](fg:color_fg2 bg:color_yellow)]($style)'

[nodejs]
symbol = ""
style = "bg:color_lightblue"
format = '[[ $symbol( $version) ](fg:color_fg3 bg:color_lightblue)]($style)'

[c]
symbol = " "
style = "bg:color_lightblue"
format = '[[ $symbol( $version) ](fg:color_fg3 bg:color_lightblue)]($style)'

[rust]
symbol = ""
style = "bg:color_lightblue"
format = '[[ $symbol( $version) ](fg:color_fg3 bg:color_lightblue)]($style)'

[golang]
symbol = ""
style = "bg:color_lightblue"
format = '[[ $symbol( $version) ](fg:color_fg3 bg:color_lightblue)]($style)'

[php]
symbol = ""
style = "bg:color_lightblue"
format = '[[ $symbol( $version) ](fg:color_fg3 bg:color_lightblue)]($style)'

[java]
symbol = ""
style = "bg:color_lightblue"
format = '[[ $symbol( $version) ](fg:color_fg3 bg:color_lightblue)]($style)'

[kotlin]
symbol = ""
style = "bg:color_lightblue"
format = '[[ $symbol( $version) ](fg:color_fg3 bg:color_lightblue)]($style)'

[haskell]
symbol = ""
style = "bg:color_lightblue"
format = '[[ $symbol( $version) ](fg:color_fg3 bg:color_lightblue)]($style)'

[python]
symbol = ""
style = "bg:color_lightblue"
format = '[[ $symbol( $version) ](fg:color_fg3 bg:color_lightblue)]($style)'

[docker_context]
symbol = ""
style = "bg:color_darkblue"
format = '[[ $symbol( $context) ](fg:color_fg4 bg:color_darkblue)]($style)'

[conda]
style = "bg:color_darkblue"
format = '[[ $symbol( $environment) ](fg:color_fg4 bg:color_darkblue)]($style)'

[time]
disabled = true

[line_break]
disabled = true

[character]
disabled = false
success_symbol = '[](bold fg:color_green)'
error_symbol = '[](bold fg:color_red)'
vimcmd_symbol = '[](bold fg:color_green)'
vimcmd_replace_one_symbol = '[](bold fg:color_purple)'
vimcmd_replace_symbol = '[](bold fg:color_purple)'
vimcmd_visual_symbol = '[](bold fg:color_yellow)'
EOF

# .zshrc
RUN cat >> "$HOME/.zshrc" <<'EOF'

# Oh-My-Zsh framework + plugins (no omz theme: Starship below owns the prompt)
export ZSH="$HOME/.oh-my-zsh"
ZSH_DISABLE_AUTO_UPDATE=1
ZSH_THEME=""
plugins=(git zsh-autosuggestions)
source $ZSH/oh-my-zsh.sh

# User-installed command line tools
export PATH="$HOME/.local/bin:$HOME/.pixi/bin:$PATH"

# Pretty prompt
eval "$(starship init zsh)"

alias ll="ls -AFGhl"
alias ..="cd .."
EOF
