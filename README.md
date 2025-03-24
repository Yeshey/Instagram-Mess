# Instagram Post Rules and Tips

**This has scripts to order images cronologically, add black lines so you can resize them in instagram as you want, and crop to make several posts look like one image**

[My instagram](https://www.instagram.com/jonnasalmeidas/)

For packages, have nix with flakes and direnv and `direnv allow` or `nix develop`

- 20 pics per post is my is my maximum

To do:

- Encontra também aquelas em que estas a trabalhar no trabalho de MTG?
- Faz referencia ao covid no post do covid?
- Also pensa se há muiscas ou não??
- E encontra uma foto da veggie canteen please xd

## In a post, aspect ratio is the same for all images

You can add black borders around images and videos in the current folder with the following command and then zoom as needed in instagram:

```sh
nix-shell -p imagemagick ffmpeg libheif --run 'mkdir -p borders; for f in *.{jpg,JPG,jpeg,JPEG,png,PNG,gif,GIF,tif,TIF,tiff,TIFF,bmp,BMP,heic,HEIC,heif,HEIF}; do [ -e "$f" ] || continue; dims=$(magick identify -format "%wx%h" "$f"); w=${dims%x*}; h=${dims#*x}; border_w=$((w * 60 / 100)); border_h=$((h * 60 / 100)); magick "$f" -bordercolor black -border ${border_w}x${border_h} "borders/bordered_$f"; done; for f in *.{kvm,KVM,avi,AVI,mp4,MP4,wmv,WMV,flv,FLV,webm,WEBM,ogg,OGG,mov,MOV,asf,ASF,mkv,MKV}; do [ -e "$f" ] || continue; ffmpeg -i "$f" -vf "pad=ceil(iw+2*iw*0.6):ceil(ih+2*ih*0.6):ceil(iw*0.6):ceil(ih*0.6):color=black" -c:a copy "borders/bordered_$f"; done'

```

Convert all heic or heif images in current folder to jpg in place (old ones go to /tmp):

```sh
nix-shell -p imagemagick libheif --run 'for f in *.{heic,HEIC,heif,HEIF}; do [ -e "$f" ] || continue; magick "$f" "${f%.*}.jpg" && (mv "$f" /tmp/ 2>/dev/null || rm "$f"); done'
```

Convert ALL images in current folder to png:

```sh
nix-shell -p imagemagick libheif --run 'for f in *.{jpg,JPG,jpeg,JPEG,png,PNG,gif,GIF,tif,TIF,tiff,TIFF,bmp,BMP,webp,WEBP,heic,HEIC,heif,HEIF}; do [ -e "$f" ] || continue; magick "$f" "${f%.*}.tmp.png" && (mv -f "$f" /tmp/ 2>/dev/null || rm -f "$f") && mv -f "${f%.*}.tmp.png" "${f%.*}.png"; done'
```

Convert ALL images in current folder to jpg with 80% compression:

```sh

```


## Extra tips

To help, you can use this command to cronologically order the pictures and videos in the current folder:

```sh
nix-shell -p exiftool --run 'bash -c "mkdir -p crono; i=1; while IFS=$'\''\t'\'' read -r dt f; do cp \"\$f\" \"crono/\${i}_\$f\"; echo \"Copied: crono/\${i}_\$f\"; i=\$((i+1)); done < <(exiftool -T -DateTimeOriginal -filename * 2>/dev/null | sort)"'
```

# Crop image to display accross several posts

## Square

Found out that in 1059 × 740, the black grid is 4 pixels long, meaning it is 0.3777148253% of the original size.

### Using 9 posts

Divide in 9 different images, and put them inside a folder called `separated`:

```sh
nix-shell -p imagemagick --run '
mkdir -p separated && convert Me-4_croppedRight.jpg \
  -crop 815x815 -gravity southeast \
  -set filename:tile "separated/%[fx:int((2444-page.y-1)/815)*3 + int((2444-page.x-1)/815) + 1]" \
  +repage +adjoin "%[filename:tile].JPG"
'
```

Reconstruct image to make sure it's okay:

```sh
nix-shell -p imagemagick --run 'files="9.JPG 8.JPG 7.JPG 6.JPG 5.JPG 4.JPG 3.JPG 2.JPG 1.JPG"; montage $files -tile 3x3 -geometry +0+0 restored_image.jpg'
```

This adds black lines to the image so you know how it looks in the end with the black lines on top (you can just open in GIMP with the rule of thirds to know where the cuts will land tho)

```sh
nix-shell -p imagemagick --run '
in="IMG_8981-darkTabled.jpg"; out="${in}_with_grid.jpg";
dims=$(identify -format "%wx%h" "$in") || { echo "Error: cannot identify image" >&2; exit 1; };
w=${dims%x*}; h=${dims#*x};
if [ "$w" -ne "$h" ]; then echo "Error: image is not square" >&2; exit 1; fi;
x1=$((w / 3)); x2=$((w * 2 / 3));
# Compute stroke width based on the ratio 4/1059 (≈0.3777%) from the original test image.
stroke=$((w * 4 / 1059));
convert "$in" -stroke black -strokewidth "$stroke" \
  -draw "line $x1,0 $x1,$w" -draw "line $x2,0 $x2,$w" \
  -draw "line 0,$x1 $w,$x1" -draw "line 0,$x2 $w,$x2" \
  "$out"
'
```

## Rectangle 

Found that the images display in the main profile as 3:4 rectangles

### Using 6 posts (you need to cut your image into 9:8 format)

crop a 9:8 image into 6 different 3:4 rectangles and put them inside "separated" folder:

We found out the preview grid is 3:4, but the image will always be cropped when uploaded to 4:5, even if you select original

You can use the given script, the script was created with assistance from deepseek-r1. It will generate separated_4x5_black_lines and separated_4x5, black_lines doesn't work correctly, you might have to pain the black sides manually. It also creates preview_grid.jpg for you to see how it will look in instagram.

Reconstruct image to make sure it's okay:

```sh
nix-shell -p imagemagick --run 'files="6.jpg 5.jpg 4.jpg 3.jpg 2.jpg 1.jpg"; montage $files -tile 3x2 -geometry +0+0 merged_image.jpg'
```
