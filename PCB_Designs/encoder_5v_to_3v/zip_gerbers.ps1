rm -r gerbers,gerbers.zip
mkdir gerbers
mv *.drl,*.gbr,*.gbr* gerbers
tar.exe -a -c -f gerbers.zip gerbers

