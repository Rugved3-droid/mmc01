# MMC-01 section 3: download once, record version + access date + file hash, freeze.
# Raw downloads land in data\raw and are treated as untrusted data (never executed).
$ErrorActionPreference = "Stop"
$raw  = "D:\mmc01\data\raw"
$prov = @()

$sources = @(
  @{ id="STRING_links";   url="https://stringdb-downloads.org/download/protein.links.v12.0/9606.protein.links.v12.0.txt.gz";     file="9606.protein.links.v12.0.txt.gz";   version="STRING v12.0 (human, 9606), combined score" },
  @{ id="STRING_info";    url="https://stringdb-downloads.org/download/protein.info.v12.0/9606.protein.info.v12.0.txt.gz";       file="9606.protein.info.v12.0.txt.gz";    version="STRING v12.0 protein info" },
  @{ id="STRING_aliases"; url="https://stringdb-downloads.org/download/protein.aliases.v12.0/9606.protein.aliases.v12.0.txt.gz"; file="9606.protein.aliases.v12.0.txt.gz"; version="STRING v12.0 protein aliases" },
  @{ id="DGIdb";          url="https://www.dgidb.org/data/latest/interactions.tsv";                                              file="dgidb_interactions.tsv";            version="DGIdb latest (see last_modified)" },
  @{ id="HGNC";           url="https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt";         file="hgnc_complete_set.txt";             version="HGNC complete set (see last_modified)" }
)

foreach ($s in $sources) {
  $dest = Join-Path $raw $s.file
  Write-Output "fetching $($s.id) ..."
  $resp = Invoke-WebRequest -Uri $s.url -OutFile $dest -PassThru -UseBasicParsing -TimeoutSec 600
  $h = (Get-FileHash -Path $dest -Algorithm SHA256).Hash.ToLower()
  $prov += [pscustomobject]@{
    id            = $s.id
    url           = $s.url
    file          = $s.file
    version       = $s.version
    last_modified = [string]$resp.Headers['Last-Modified']
    bytes         = (Get-Item $dest).Length
    sha256        = $h
    accessed_utc  = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  }
  Write-Output "  $($s.id)  bytes=$((Get-Item $dest).Length)  sha256=$h"
}

$prov | ConvertTo-Json -Depth 4 | Out-File -FilePath (Join-Path $raw "PROVENANCE.json") -Encoding utf8
Write-Output "DONE - PROVENANCE.json written"
