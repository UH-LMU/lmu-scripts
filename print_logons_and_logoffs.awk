{
FS=","
split($11,fields,"|")  
if ($5=="4647")
{
	print $2,"\t", $3, "\tLogoff\t", fields[2]
} 
else if ($5=="4648")
{
	print $2,"\t", $3, "\tLogon\t", fields[6]
}
}

