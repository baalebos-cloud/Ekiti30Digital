<#
EKITI@30 - Batch import of candidate images into 16_Media/Culture_Tourism

Run this from the ROOT of your repo (where the 16_Media folder lives):
    cd C:\Users\l2e\Ekiti30Digital
    .\Import-CandidateImages.ps1

What it does, per entry:
  1. Downloads the candidate image into that entry's media\ folder as
     CANDIDATE_<slug>.<ext> (prefixed so it's obviously not cleared yet)
  2. Updates that entry's metadata.md "File name:" line to match
  3. Leaves "Copyright/permission status:" untouched -- downloading is NOT
     the same as clearing permission

Entries flagged REJECT / DO NOT USE in ASSET_SOURCE_REVIEW.md are
deliberately SKIPPED -- see the reason printed for each. This includes:
  - CT-006, 016, 017, 018, 019, 024, 025, 026, 027, PENDING-01, PENDING-02:
    Google Images thumbnail cache links (broken/no source/no license)
  - CT-009: images.openai.com is an AI-IMAGE-GENERATION host, not a real
    photo -- this is almost certainly a fabricated image, never use it
  - CT-013: HENI art-market platform -- high copyright/legal risk
  - CT-022: filename references a Sotheby's auction lot -- high
    copyright/legal risk
  - CT-004: no candidate link exists yet (needs direct business outreach)

If you disagree with a skip and want to download one of these anyway for
your own reference, do it manually -- this script won't do it for you.
#>

$ErrorActionPreference = "Stop"

# Mimic a browser UA -- some sites (news outlets, WordPress) block the
# default PowerShell user-agent string.
$headers = @{ "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) EKITI30-DIGITAL-MediaBot/1.0" }

$entries = @(
    @{ Id="CT-001"; Slug="ikogosi-warm-springs";                         Url="https://upload.wikimedia.org/wikipedia/commons/f/f6/Ikogosi-Ekiti_warm_spring_03.jpg"; Ext="jpg" }
    @{ Id="CT-002"; Slug="arinta-waterfall";                             Url="https://upload.wikimedia.org/wikipedia/commons/1/1e/Arinta_Waterfall%2C_Ipole_Iloro3.jpg"; Ext="jpg" }
    @{ Id="CT-003"; Slug="fajuyi-memorial-park";                         Url="https://upload.wikimedia.org/wikipedia/commons/c/cb/Fajuyi_Memorial_Park%2C_Ado_Ekiti_8.jpg"; Ext="jpg" }
    @{ Id="CT-005"; Slug="ewi-of-ado-ekiti-palace";                      Url="https://upload.wikimedia.org/wikipedia/commons/0/02/Ewi_of_Ado-Ekiti_Palace%2C_Ado-Ekiti%2C_Ekiti_State.jpg"; Ext="jpg" }
    @{ Id="CT-007"; Slug="abanijorin-rock-cave";                         Url="https://nigerianheritage.ng/img/tours/6867e93dc6825_ar11.webp"; Ext="webp" }
    @{ Id="CT-008"; Slug="esa-cave";                                     Url="https://newtelegraphng.com/wp-content/uploads/2024/12/Esa-Cave-1.jpg"; Ext="jpg" }
    @{ Id="CT-010"; Slug="egbe-dam";                                     Url="https://independent.ng/wp-content/uploads/2019/11/Egbe-Dam-Ekiti-State-1.jpg"; Ext="jpg" }
    @{ Id="CT-011"; Slug="olosunta-orole-hills";                         Url="https://fmicgovng.s3.amazonaws.com/cityhill/wp-content/uploads/2019/10/7-1.jpg"; Ext="jpg" }
    @{ Id="CT-012"; Slug="erin-ayonigba-sacred-fish-river";              Url="https://lifestyle.thecable.ng/wp-content/uploads/2017/10/Erin-Ayonigba-Fish-River.jpg"; Ext="jpg" }
    @{ Id="CT-014"; Slug="ado-ni-ile-ifa-ado-ekitis-ifa-heritage";       Url="https://upload.wikimedia.org/wikipedia/commons/7/79/Ifa_and_Orisa_pilgrimage_in_Ekiti._03.jpg"; Ext="jpg" }
    @{ Id="CT-015"; Slug="olosunta-and-orole-hill-deity-veneration";     Url="https://pbs.twimg.com/media/EibhUNSWkAIaWlk.jpg"; Ext="jpg" }
    @{ Id="CT-020"; Slug="epa-masquerade-festival-isan-ekiti";           Url="https://www.isanekiti.com/storage/festivals/gallery/uDgVyG8EhuOxjmj00eVIpmy8Fm7qeG3UaUgtWBFd.jpg"; Ext="jpg" }
    @{ Id="CT-021"; Slug="aeregbe-festival-afao-ekiti";                  Url="https://culturematters.art.blog/wp-content/uploads/2022/08/img-20220831-wa0024.jpg"; Ext="jpg" }
    @{ Id="CT-023"; Slug="olowe-of-ise-sculpture-legacy";                Url="https://oloweofise.com/wp-content/uploads/2024/10/WhatsApp-Image-2024-10-20-at-14.27.06_80ac00c9.jpg"; Ext="jpg" }
)

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

foreach ($e in $entries) {
    $folder = Join-Path "16_Media\Culture_Tourism\$($e.Slug)" "media"
    $metaPath = Join-Path "16_Media\Culture_Tourism\$($e.Slug)" "metadata.md"
    $fileName = "CANDIDATE_$($e.Slug).$($e.Ext)"
    $outPath = Join-Path $folder $fileName

    if (-not (Test-Path $folder)) {
        Write-Host "[$($e.Id)] SKIP -- folder not found: $folder (check your slug/folder structure matches)" -ForegroundColor Yellow
        continue
    }

    try {
        Invoke-WebRequest -Uri $e.Url -OutFile $outPath -Headers $headers
        $size = (Get-Item $outPath).Length
        if ($size -lt 1000) {
            Write-Host "[$($e.Id)] WARNING -- downloaded but file is only $size bytes, likely an error page, not a real image. Check manually." -ForegroundColor Yellow
        } else {
            Write-Host "[$($e.Id)] Downloaded ($size bytes) -> $outPath" -ForegroundColor Green
            $downloaded++
        }

        if (Test-Path $metaPath) {
            (Get-Content $metaPath -Raw) -replace "File name:.*", "File name: $fileName" | Set-Content $metaPath -NoNewline
            Write-Host "[$($e.Id)] Updated metadata.md file name field" -ForegroundColor Green
        } else {
            Write-Host "[$($e.Id)] WARNING -- metadata.md not found at $metaPath" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[$($e.Id)] FAILED to download: $($_.Exception.Message)" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "--- Skipped by design (see ASSET_SOURCE_REVIEW.md for full reasoning) ---" -ForegroundColor Cyan
foreach ($s in $skipped) {
    Write-Host "[$($s.Id)] SKIPPED -- $($s.Reason)" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "Done. Downloaded: $downloaded | Failed: $failed | Deliberately skipped: $($skipped.Count)" -ForegroundColor Cyan
Write-Host "Remember: every downloaded file is still 'Needs verification/permission' -- check permission.md before publishing anything." -ForegroundColor Cyan
