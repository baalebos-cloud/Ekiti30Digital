<#
EKITI@30 - Candidate image acquisition utility for 16_Media/Culture_Tourism

PURPOSE (per review from @smartexploit on PR #42):
This script is a CANDIDATE IMAGE ACQUISITION UTILITY ONLY. It downloads
leads found during source research into each entry's media\ folder so they
can be reviewed. It is NOT a copyright/licence verification tool and does
NOT approve anything for publication. Downloading a file here never changes
"Copyright/permission status" in metadata.md, and never marks an entry
Verified. That status is set manually, only after the project's media
verification workflow (permission.md: request sent -> response logged ->
rights confirmed) is complete.

Full reasoning for every skip/include decision in this script lives in:
    16_Media/Culture_Tourism/ASSET_SOURCE_REVIEW.md
(that file must exist in the repo for these decisions to be reproducible --
see PR #42 review point 1. If you're reading this and that file is missing,
stop and add it before relying on this script's skip list.)

USAGE:
    Run from the ROOT of the repo (where 16_Media lives):
        .\Import-CandidateImages.ps1                 # skips files that already exist
        .\Import-CandidateImages.ps1 -Force           # re-downloads and overwrites existing candidates
#>

param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$headers = @{ "User-Agent" = "EKITI30DIGITAL-MediaBot/1.0 (https://github.com/smartexploit/Ekiti30Digital; contact: paulayomide350@gmail.com)" }

# Known magic bytes for the image formats we expect. Used to catch cases
# where a server returns HTML (e.g. an error/redirect page) with a 200
# status and/or a misleading Content-Type header.
$magicBytes = @{
    "jpg"  = ,@(0xFF, 0xD8, 0xFF)
    "jpeg" = ,@(0xFF, 0xD8, 0xFF)
    "png"  = ,@(0x89, 0x50, 0x4E, 0x47)
    "webp" = ,@(0x52, 0x49, 0x46, 0x46)   # "RIFF" -- WEBP marker sits a few bytes further in, RIFF check is a reasonable first gate
}

function Test-IsImageFile {
    param([string]$Path, [string]$Ext)

    if (-not (Test-Path $Path)) { return $false }
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -lt 8) { return $false }

    $expected = $magicBytes[$Ext.ToLower()]
    if (-not $expected) { return $true }  # unknown ext, skip magic-byte check rather than false-reject

    for ($i = 0; $i -lt $expected.Length; $i++) {
        if ($bytes[$i] -ne $expected[$i]) { return $false }
    }
    return $true
}

$entries = @(
    @{ Id="CT-001"; Slug="ikogosi-warm-springs";                         Url="https://upload.wikimedia.org/wikipedia/commons/f/f6/Ikogosi-Ekiti_warm_spring_03.jpg"; Ext="jpg" }
    @{ Id="CT-002"; Slug="arinta-waterfall";                             Url="https://upload.wikimedia.org/wikipedia/commons/1/1e/Arinta_Waterfall%2C_Ipole_Iloro3.jpg"; Ext="jpg" }
    @{ Id="CT-003"; Slug="fajuyi-memorial-park";                         Url="https://upload.wikimedia.org/wikipedia/commons/c/cb/Fajuyi_Memorial_Park%2C_Ado_Ekiti_8.jpg"; Ext="jpg" }
    @{ Id="CT-005"; Slug="ewi-of-ado-ekiti-palace";                      Url="https://upload.wikimedia.org/wikipedia/commons/0/02/Ewi_of_Ado-Ekiti_Palace%2C_Ado-Ekiti%2C_Ekiti_State.jpg"; Ext="jpg" }
    @{ Id="CT-007"; Slug="abanijorin-rocks-cave";                        Url="https://nigerianheritage.ng/img/tours/6867e93dc6825_ar11.webp"; Ext="webp" }
    @{ Id="CT-008"; Slug="esa-cave";                                     Url="https://newtelegraphng.com/wp-content/uploads/2024/12/Esa-Cave-1.jpg"; Ext="jpg" }
    @{ Id="CT-010"; Slug="egbe-dam";                                     Url="https://independent.ng/wp-content/uploads/2019/11/Egbe-Dam-Ekiti-State-1.jpg"; Ext="jpg" }
    @{ Id="CT-011"; Slug="olosunta-orole-hills";                         Url="https://fmicgovng.s3.amazonaws.com/cityhill/wp-content/uploads/2019/10/7-1.jpg"; Ext="jpg" }
    @{ Id="CT-012"; Slug="erin-ayonigba-sacred-fish-river";              Url="https://lifestyle.thecable.ng/wp-content/uploads/2017/10/Erin-Ayonigba-Fish-River.jpg"; Ext="jpg" }
    @{ Id="CT-014"; Slug="ado-ni-ile-ifa-ado-ekiti-s-ifa-heritage";      Url="https://upload.wikimedia.org/wikipedia/commons/7/79/Ifa_and_Orisa_pilgrimage_in_Ekiti._03.jpg"; Ext="jpg" }
    @{ Id="CT-015"; Slug="olosunta-and-orole-hill-deity-veneration";     Url="https://pbs.twimg.com/media/EibhUNSWkAIaWlk.jpg"; Ext="jpg" }
    @{ Id="CT-020"; Slug="epa-masquerade-festival-isan-ekiti";           Url="https://www.isanekiti.com/storage/festivals/gallery/uDgVyG8EhuOxjmj00eVIpmy8Fm7qeG3UaUgtWBFd.jpg"; Ext="jpg" }
    @{ Id="CT-021"; Slug="aeregbe-festival";                             Url="https://culturematters.art.blog/wp-content/uploads/2022/08/img-20220831-wa0024.jpg"; Ext="jpg" }
    @{ Id="CT-023"; Slug="olowe-of-ise-sculpture-legacy";                Url="https://oloweofise.com/wp-content/uploads/2024/10/WhatsApp-Image-2024-10-20-at-14.27.06_80ac00c9.jpg"; Ext="jpg" }
)

# See ASSET_SOURCE_REVIEW.md for full reasoning behind every skip below --
# this list is a pointer to that document, not a substitute for it.
$skipped = @(
    @{ Id="CT-004"; Reason="No candidate link found yet -- needs direct business outreach, not a download" }
    @{ Id="CT-006"; Reason="Google Images thumbnail cache -- no source, no license, unusable" }
    @{ Id="CT-009"; Reason="AI-GENERATED image (images.openai.com) -- not a real photo, never use" }
    @{ Id="CT-013"; Reason="HENI art-market platform -- high copyright/legal risk, do not use" }
    @{ Id="CT-016"; Reason="Google Images thumbnail cache -- unusable" }
    @{ Id="CT-017"; Reason="Google Images thumbnail cache -- unusable" }
    @{ Id="CT-018"; Reason="Google Images thumbnail cache -- unusable" }
    @{ Id="CT-019"; Reason="Google Images thumbnail cache -- unusable" }
    @{ Id="CT-022"; Reason="Filename references a Sotheby's auction lot -- high copyright/legal risk, do not use" }
    @{ Id="CT-024"; Reason="Google Images thumbnail cache -- unusable" }
    @{ Id="CT-025"; Reason="Google Images thumbnail cache -- unusable" }
    @{ Id="CT-026"; Reason="Google Images thumbnail cache -- unusable" }
    @{ Id="CT-027"; Reason="Google Images thumbnail cache -- unusable" }
    @{ Id="CT-PENDING-01"; Reason="Google Images thumbnail cache -- unusable" }
    @{ Id="CT-PENDING-02"; Reason="Google Images thumbnail cache -- unusable" }
)

$downloaded = 0
$failed = 0
$alreadyExists = 0
$invalidResponse = 0

foreach ($e in $entries) {
    $folder = Join-Path "16_Media\Culture_Tourism\$($e.Slug)" "media"
    $metaPath = Join-Path "16_Media\Culture_Tourism\$($e.Slug)" "metadata.md"
    $fileName = "CANDIDATE_$($e.Slug).$($e.Ext)"
    $outPath = Join-Path $folder $fileName

    if (-not (Test-Path $folder)) {
        Write-Host "[$($e.Id)] SKIP -- folder not found: $folder (check your slug/folder structure matches)" -ForegroundColor Yellow
        continue
    }

    # --- Review point 2: don't silently overwrite an existing candidate ---
    if ((Test-Path $outPath) -and (-not $Force)) {
        Write-Host "[$($e.Id)] SKIP -- $fileName already exists. Re-run with -Force to replace it." -ForegroundColor DarkCyan
        $alreadyExists++
        continue
    }

    # --- Download to a temp path first; never touch the real file or
    #     metadata.md until validation passes ---
    $tempPath = "$outPath.tmp"
    try {
        Invoke-WebRequest -Uri $e.Url -OutFile $tempPath -Headers $headers
    } catch {
        Write-Host "[$($e.Id)] FAILED to download: $($_.Exception.Message)" -ForegroundColor Red
        $failed++
        if (Test-Path $tempPath) { Remove-Item $tempPath -Force }
        continue
    }

    # --- Review point 3: validate it's actually an image, not an HTML/
    #     error page, before accepting the download ---
    $size = (Get-Item $tempPath).Length
    $isImage = Test-IsImageFile -Path $tempPath -Ext $e.Ext

    if ($size -lt 1000 -or -not $isImage) {
        Write-Host "[$($e.Id)] REJECTED -- downloaded content failed image validation (size: $size bytes, magic-byte check: $isImage). Likely an error/redirect page, not a real image. Not saved, metadata.md left untouched." -ForegroundColor Red
        Remove-Item $tempPath -Force
        $invalidResponse++
        continue
    }

    Move-Item $tempPath $outPath -Force
    Write-Host "[$($e.Id)] Downloaded and validated ($size bytes) -> $outPath" -ForegroundColor Green
    $downloaded++

    # --- Review point 4: only touch File name, never Copyright/permission
    #     status or Verification status -- and only after validation ---
    if (Test-Path $metaPath) {
        (Get-Content $metaPath -Raw) -replace "File name:.*", "File name: $fileName" | Set-Content $metaPath -NoNewline
        Write-Host "[$($e.Id)] Updated metadata.md file name field only (permission/verification status untouched)" -ForegroundColor Green
    } else {
        Write-Host "[$($e.Id)] WARNING -- metadata.md not found at $metaPath" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "--- Skipped by design (see 16_Media/Culture_Tourism/ASSET_SOURCE_REVIEW.md for full reasoning) ---" -ForegroundColor Cyan
foreach ($s in $skipped) {
    Write-Host "[$($s.Id)] SKIPPED -- $($s.Reason)" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "Done. Downloaded: $downloaded | Already existed (use -Force to replace): $alreadyExists | Failed to fetch: $failed | Rejected (not a valid image): $invalidResponse | Deliberately skipped: $($skipped.Count)" -ForegroundColor Cyan
Write-Host "Reminder: this script only ever sets 'File name'. Copyright/permission status and Verification status are set manually via the project's media verification workflow -- see permission.md in each entry." -ForegroundColor Cyan
