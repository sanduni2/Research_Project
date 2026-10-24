$ErrorActionPreference = 'Stop'

$projectRoot = "D:/Research"
$inputPath = Join-Path $projectRoot "FINAL_THESIS_UPDATED.md"
$outputPath = Join-Path $projectRoot "FINAL_THESIS_UPDATED.docx"

if (-not (Test-Path $inputPath)) {
    throw "Input file not found: $inputPath"
}

$lines = Get-Content -Path $inputPath -Encoding UTF8

# Word constants
$wdStory = 6
$wdSeekMainDocument = 0
$wdHeaderFooterPrimary = 1
$wdSectionBreakNextPage = 2
$wdLineSpaceSingle = 0
$wdLineSpace1pt5 = 1
$wdAlignPageNumberCenter = 1
$wdAlignPageNumberRight = 2
$wdPageNumberStyleLowercaseRoman = 2
$wdPageNumberStyleArabic = 0

$word = New-Object -ComObject Word.Application
$word.Visible = $false

try {
    $doc = $word.Documents.Add()

    # A4 and margins per SLIIT guide (mm to points)
    $doc.PageSetup.PaperSize = 7
    $doc.PageSetup.TopMargin = 25 * 2.83464567
    $doc.PageSetup.BottomMargin = 40 * 2.83464567
    $doc.PageSetup.LeftMargin = 40 * 2.83464567
    $doc.PageSetup.RightMargin = 25 * 2.83464567

    $sel = $word.Selection

    # Global body style
    $sel.WholeStory()
    $sel.Font.Name = "Times New Roman"
    $sel.Font.Size = 12
    $sel.Font.Bold = 0
    $sel.ParagraphFormat.LineSpacingRule = $wdLineSpace1pt5
    $sel.EndKey($wdStory) | Out-Null

    # Build content from markdown with basic styling rules
    foreach ($rawLine in $lines) {
        $line = $rawLine.TrimEnd()

        if ($line -eq "---") {
            $sel.InsertParagraphAfter()
            $sel.InsertParagraphAfter()
            continue
        }

        if ([string]::IsNullOrWhiteSpace($line)) {
            $sel.InsertParagraphAfter()
            continue
        }

        # Images: ![caption](path)
        if ($line -match '^!\[(.*)\]\((.*)\)$') {
            $imgPath = $Matches[2]
            $absImg = Join-Path $projectRoot $imgPath
            if (Test-Path $absImg) {
                $sel.InlineShapes.AddPicture($absImg) | Out-Null
                $sel.ParagraphFormat.Alignment = 1
                $sel.InsertParagraphAfter()
                $sel.ParagraphFormat.Alignment = 0
            }
            continue
        }

        # Table rows in markdown
        if ($line -match '^\|.*\|$') {
            $clean = ($line -replace '^\|','' -replace '\|$','')
            $cells = $clean.Split('|') | ForEach-Object { $_.Trim() }
            $sel.TypeText(($cells -join "`t"))
            $sel.InsertParagraphAfter()
            continue
        }

        # Bullet list
        if ($line -match '^\s*-\s+') {
            $text = $line -replace '^\s*-\s+',''
            $sel.TypeText("• " + $text)
            $sel.InsertParagraphAfter()
            continue
        }

        $isChapter = $line -match '^CHAPTER\s+[0-9]+:'
        $isSection = $line -match '^[0-9]+\.[0-9]+\s+'
        $isSubSection = $line -match '^[0-9]+\.[0-9]+\.[0-9]+\s+'

        if ($isChapter) {
            $sel.Font.Name = "Times New Roman"
            $sel.Font.Size = 14
            $sel.Font.Bold = 1
            $sel.TypeText($line.ToUpper())
            $sel.InsertParagraphAfter()
            $sel.InsertParagraphAfter()
            $sel.Font.Size = 12
            $sel.Font.Bold = 0
            continue
        }

        if ($isSubSection -or $isSection) {
            $sel.Font.Name = "Times New Roman"
            $sel.Font.Size = 12
            $sel.Font.Bold = 1
            $sel.TypeText($line)
            $sel.InsertParagraphAfter()
            $sel.Font.Bold = 0
            continue
        }

        if ($line -match '^[A-Z][A-Z\s:&\-]+$') {
            $sel.Font.Name = "Times New Roman"
            $sel.Font.Size = 14
            $sel.Font.Bold = 1
            $sel.TypeText($line)
            $sel.InsertParagraphAfter()
            $sel.InsertParagraphAfter()
            $sel.Font.Size = 12
            $sel.Font.Bold = 0
            continue
        }

        $sel.Font.Name = "Times New Roman"
        $sel.Font.Size = 12
        $sel.Font.Bold = 0
        $sel.TypeText($line)
        $sel.InsertParagraphAfter()
    }

    # Section and page numbering setup
    # Section 1: Title page (no page number)
    $sel.EndKey($wdStory) | Out-Null
    $sel.HomeKey($wdStory) | Out-Null

    # Find ABSTRACT and create section break before it for preliminary pages
    $find = $word.Selection.Find
    $find.ClearFormatting()
    $find.Text = "ABSTRACT"
    if ($find.Execute()) {
        $word.Selection.InsertBreak($wdSectionBreakNextPage)
    }

    # Find first chapter and create section break before it for Arabic numbering
    $find2 = $word.Selection.Find
    $find2.ClearFormatting()
    $find2.Text = "CHAPTER 1: INTRODUCTION"
    if ($find2.Execute()) {
        $word.Selection.InsertBreak($wdSectionBreakNextPage)
    }

    # Ensure sections are unlinked for footers and apply pagination
    if ($doc.Sections.Count -ge 2) {
        $doc.Sections.Item(2).Footers.Item($wdHeaderFooterPrimary).LinkToPrevious = $false
        $pn2 = $doc.Sections.Item(2).Footers.Item($wdHeaderFooterPrimary).PageNumbers
        $null = $pn2.Add($wdAlignPageNumberCenter)
        $pn2.NumberStyle = $wdPageNumberStyleLowercaseRoman
        $pn2.RestartNumberingAtSection = $true
        $pn2.StartingNumber = 1
    }

    if ($doc.Sections.Count -ge 3) {
        $doc.Sections.Item(3).Footers.Item($wdHeaderFooterPrimary).LinkToPrevious = $false
        $pn3 = $doc.Sections.Item(3).Footers.Item($wdHeaderFooterPrimary).PageNumbers
        $null = $pn3.Add($wdAlignPageNumberRight)
        $pn3.NumberStyle = $wdPageNumberStyleArabic
        $pn3.RestartNumberingAtSection = $true
        $pn3.StartingNumber = 1
    }

    # Abstract single spacing requirement
    $range = $doc.Content
    $findAbstract = $range.Find
    $findAbstract.ClearFormatting()
    $findAbstract.Text = "ABSTRACT"
    if ($findAbstract.Execute()) {
        $absStart = $range.Start
        $range2 = $doc.Range($absStart, $doc.Content.End)
        $findAck = $range2.Find
        $findAck.ClearFormatting()
        $findAck.Text = "ACKNOWLEDGEMENTS"
        if ($findAck.Execute()) {
            $abstractBody = $doc.Range($absStart, $range2.Start)
            $abstractBody.ParagraphFormat.LineSpacingRule = $wdLineSpaceSingle
            $abstractBody.Font.Size = 11
        }
    }

    $doc.SaveAs($outputPath)
    $doc.Close()
}
finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
}

Write-Output "Created: $outputPath"
