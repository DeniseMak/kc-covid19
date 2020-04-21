[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  $nytDataPath,
  $state = "Nebraska")

$countyFilePath = join-path $nytDataPath "us-counties.csv"
$statesFilePath = join-path $nytDataPath "us-states.csv"

$data = import-csv $countyFilePath
$dstr = $data[-1].date

$counties = $data | 
  where {$_.date -eq $dstr} |
  where {$_.state -eq $state} |
  select -prop county,cases,deaths

$counties | ft

$data = import-csv $statesFilePath

$stateData = $data | where {$_.state -eq $state}
$stateData | select -prop date,cases,deaths | ft

$last = $stateData[0]

$stateData | 
  select -skip 1 | 
  foreach { 
      $_ | 
        select -prop date,@{name="newCases";expression={$_.cases - $last.cases}},cases,deaths; 
        $last=$_
  } | ft
