[app]
title = Engineering Scientific Calculator V2
package.name = engscicalcv2
package.domain = org.engineeringcalculator
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,md
version = 2.0.0
requirements = python3,kivy==2.3.1
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
api = 35
minapi = 23
android.archs = arm64-v8a, armeabi-v7a
android.permissions =
