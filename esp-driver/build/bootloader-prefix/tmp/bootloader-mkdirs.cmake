# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "D:/Espressif/frameworks/esp-idf-v5.3/components/bootloader/subproject"
  "R:/ROP/ROP-Audio-Vibration/esp-driver/build/bootloader"
  "R:/ROP/ROP-Audio-Vibration/esp-driver/build/bootloader-prefix"
  "R:/ROP/ROP-Audio-Vibration/esp-driver/build/bootloader-prefix/tmp"
  "R:/ROP/ROP-Audio-Vibration/esp-driver/build/bootloader-prefix/src/bootloader-stamp"
  "R:/ROP/ROP-Audio-Vibration/esp-driver/build/bootloader-prefix/src"
  "R:/ROP/ROP-Audio-Vibration/esp-driver/build/bootloader-prefix/src/bootloader-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "R:/ROP/ROP-Audio-Vibration/esp-driver/build/bootloader-prefix/src/bootloader-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "R:/ROP/ROP-Audio-Vibration/esp-driver/build/bootloader-prefix/src/bootloader-stamp${cfgdir}") # cfgdir has leading slash
endif()
