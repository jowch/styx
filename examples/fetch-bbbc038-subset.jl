#!/usr/bin/env julia
# Optional pre-fetch for examples/cell-seg-demo.jl
# Downloads BBBC038 stage1_train.zip once, extracts N image folders into the demo cache.
# Uses only Julia stdlib + system `unzip`/`zipinfo` (no package resolve).
#
# Usage:
#   julia examples/fetch-bbbc038-subset.jl
#   julia examples/fetch-bbbc038-subset.jl 12

using Downloads

const ZIP_URL = "https://data.broadinstitute.org/bbbc/BBBC038/stage1_train.zip"
const N = length(ARGS) >= 1 ? parse(Int, ARGS[1]) : 8
const CACHE = joinpath(homedir(), ".cache", "styx-bbbc038-demo")
const ZIP_PATH = joinpath(CACHE, "stage1_train.zip")
const SUBSET_DIR = joinpath(CACHE, "subset")

function ensure_zip!()
	mkpath(CACHE)
	if isfile(ZIP_PATH)
		@info "Using cached zip" path = ZIP_PATH
		return ZIP_PATH
	end
	@info "Downloading BBBC038 stage1_train (~83 MB)" url = ZIP_URL dest = ZIP_PATH
	Downloads.download(ZIP_URL, ZIP_PATH)
	return ZIP_PATH
end

function list_image_ids(zip_path::AbstractString)
	out = read(`zipinfo -1 $(zip_path)`, String)
	ids = Set{String}()
	for line in eachline(IOBuffer(out))
		parts = split(line, '/')
		!isempty(parts[1]) && push!(ids, parts[1])
	end
	return sort!(collect(ids))
end

function extract_subset!(zip_path::AbstractString, ids, out_dir::AbstractString)
	mkpath(out_dir)
	# Build argv explicitly so each glob is a separate argument.
	patterns = ["$id/*" for id in ids]
	cmd = Cmd(vcat(["unzip", "-n", "-q", zip_path], patterns, ["-d", out_dir]))
	run(cmd)
	return out_dir
end

function main()
	Sys.which("unzip") === nothing && error("`unzip` not found on PATH (needed for selective extract)")
	Sys.which("zipinfo") === nothing && error("`zipinfo` not found on PATH")
	zip_path = ensure_zip!()
	ids = list_image_ids(zip_path)
	n = clamp(N, 1, length(ids))
	chosen = ids[1:n]
	extract_subset!(zip_path, chosen, SUBSET_DIR)
	println("Extracted $n images → $SUBSET_DIR")
	for id in chosen
		println("  ", id)
	end
end

main()
