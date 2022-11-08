#!/bin/bash

aesX="aes_sw"
len=${#1}
aesstep=16

rm cipher.txt

echo $len
echo $aesX
echo $aesstep

for i in $(seq 0 $aesstep $len)
do
./$aesX ${1:i:$(($i+16))} > tempAES.txt
echo ${1:i:$(($i+16))}
grep "CIPHERTEXT: " -n tempAES.txt > tempres.txt
cut -c 34- tempres.txt >> cipher.txt


rm tempAES.txt
rm tempres.txt

echo $i
echo $(($i+16))
done

./$aesX $1 > tempAES.txt
grep "CIPHERTEXT: " -n tempAES.txt > tempres.txt
cut -c 34- tempres.txt > cipher_1.txt

rm tempAES.txt
rm tempres.txt
