#!/bin/bash

aesX="aes_sw"
len=${#1}
aesstep=16

rm cipher.txt

for i in $(seq 0 $aesstep $len)
do
./$aesX ${1:i:$(($i+16))} > tempAES.txt
grep "CIPHERTEXT: " -n tempAES.txt > tempres.txt
cut -c 34- tempres.txt >> cipher_16B.txt


rm tempAES.txt
rm tempres.txt

done

