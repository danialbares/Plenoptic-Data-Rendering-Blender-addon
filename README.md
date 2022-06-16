# Plenoptic Data Rendering Blender Add-on
This repository contains a Blender add-on to generate and render Plenoptic data in multiple modalities (Light Field and Point Cloud). The features included in the tool are:

1. Light Field

- View Rendering with depth and disparity maps (obtained from the addon https://github.com/tbaust/lightfield-blender-addon)
- Focus stack generation
- Depth and disparity map format conversion (PFM & PNG)
- Lenslet image generation
- Side-by-side image generation (center view + depth map)

2. Point Cloud

- Cloud generation from previously rendered views
- Cloud rendering from Blender scene

3. Software optimization

- Automatic Python dependencies installation


## Installation
In order to successfully install this add-on you must follow the next steps:

1. Download the ZIP file from this repository containing the code
2. Unzip the file (if not already) and create an empty folder inside it with the name "lib"
3. ZIP the file again and install it in Blender through File -> Preferences -> Add-ons -> Install -> Select the corresponding ZIP
4. Go to File -> Preferences -> File Paths -> Temporary files and include a temporary folder (is not done previously)
5. Go back to File -> Preferences -> Add-ons, enable the add-on with the checkbox and open the dropdown menu
6. Click on "Install missing dependencies" and wait momentarily

The add-on should be ready to use!


## License
This work, "Plenoptic Data Rendering", is a derivative of "4D Light Field Benchmark" by Katrin Honauer & Ole Johannsen used under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (www.creativecommons.org/licenses/by-nc-sa/4.0/) and "Stanford PLY Format" by Bruce Merry & Campbell Barton used under GNU General Public License version 3.0 (GPLv3)(www.gnu.org/licenses/gpl-3.0.html) / Desaturated from original.

"Plenoptic Data Rendering" is licensed under GPLv3 (www.gnu.org/licenses/gpl-3.0.html) by Daniel Albares Martin



