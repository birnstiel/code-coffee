using Pkg
Pkg.activate(".")
Pkg.instantiate()

@info "loading packages"
@time using BenchmarkTools
using Random
@info "done"

function estimate_pi(nMC)

    radius   = 1.0
    diameter = 2radius
    n_circle = 0
    
    @inbounds for _ ∈ 1:nMC
        x = (rand() - 0.5) * diameter
        y = (rand() - 0.5) * diameter
        r = √(x^2 + y^2)
        if r <= radius
           n_circle += 1
        end
    end
    
    return 4n_circle/nMC
end

nMC = 1_000_000


@info "First function call"
@time estimate_pi(nMC)

@info "Second function call"
@time estimate_pi(nMC)

@info "benchmark:"
@btime estimate_pi(nMC)

@info "L1 error: $( abs(estimate_pi(nMC) - π) / π )"
