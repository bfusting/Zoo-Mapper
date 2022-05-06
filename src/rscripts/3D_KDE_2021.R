# Load Required Libraries
library (ks)
library (rgl)
library (misc3d)
library (readxl)
library (dplyr)
library (htmlwidgets)
library(ggplot2)
library(rjson)

pandoc_path <- Sys.getenv("RSTUDIO_PANDOC")
Sys.setenv(RSTUDIO_PANDOC="C:/Program Files/RStudio/bin/pandoc")

options(stringsAsFactors = FALSE)

# Define Functions
calcKernelVol <- function(fhat, perc) { # Calculates perc% kernel volume
  ct <- contourLevels(fhat, cont=perc, approx=TRUE)
  vol.voxel <- prod(sapply(fhat$eval.points, diff)[1,]) # Calculate volume of single voxel
  no.voxel <- sum(fhat$estimate>ct) # Calculate number of voxels
  vol <- no.voxel*vol.voxel # Calculate total volume as product
  return(vol) }

calcIntersect <- function(fhat1, fhat2, perc) { # Calculates volume of intersection of perc% volumes
  ct1 <- contourLevels(fhat1, cont=perc, approx=TRUE) 
  ct2 <- contourLevels(fhat2, cont=perc, approx=TRUE) 
  vol.voxel <- prod(sapply(fhat1$eval.points, diff)[1,]) 
  no.voxel <- sum(fhat1$estimate>ct1 & fhat2$estimate>ct2) 
  intersect <- no.voxel*vol.voxel
  return(intersect) }

genLabel <- function(m, n, pilot) { # Generate label for KDE settings
  return(paste("M",m,",N",n,",",pilot,sep="")) }

genBounds <- function(data1, data2, if2D) { # Generate bounds for two volumes
  data <- rbind(data1, data2)
  mins <- c()
  maxs <- c()
  if(if2D) {
    mins <- c(min(data$X), min(data$Y))
    maxs <- c(max(data$X), max(data$Y)) }
  else {
    mins <- c(min(data$X), min(data$Y), min(data$Z))
    maxs <- c(max(data$X), max(data$Y), max(data$Z)) }
  bounds <- c(mins, maxs)
  return(bounds) }

KDETrialSingle <- function(data, if2D, percs, m, n, pilot, imgDir, colorSingle, opacitySingle, display2D) { # Tries KDE with given settings for single volumes
  band <- Hpi(data, nstage=n, pilot=pilot)*m # Generate bandwidth matrix
  fhat <- kde(data, H=band) # Generate KDE
  if(typeof(fhat$x) == "list") { fhat$x  <- data.matrix(fhat$x) } # Convert data type to avoid sample size limit
  if(if2D) { # Create and save 2D plot
    imgName <- paste(imgDir,"/",genLabel(m,n,pilot),".png",sep="")
    png(imgName)
    print(paste("imgName", imgName, sep=" "))
    plot(fhat, display=display2D, cont=percs, asp=1, col=colorSingle)
    dev.off()
  }
  else { # Create and save 3D widget
    imgName <- paste(imgDir,"/",genLabel(m,n,pilot),".html",sep="")
    plot(fhat, display="rgl", cont=percs, asp=1, col=colorSingle, alpha=opacitySingle)
    scene <- scene3d()
    saveWidget(rglwidget(scene), file=imgName)
    rgl.close() }
  vols <- vector()
  for(perc in percs) { vols <- append(vols, calcKernelVol(fhat,perc)) } # Store calculated volumes
  return(vols) }


KDETrialDouble <- function(data1, data2, if2D, percs, m, n, pilot, imgDir, colorDouble1, colorDouble2, opacityDouble1, opacityDouble2, display2D) { # Tries KDE with given settings for two volumes
  band1 <- Hpi(data1, nstage=n, pilot=pilot)*m
  band2 <- Hpi(data2, nstage=n, pilot=pilot)*m
  bounds <- genBounds(data1, data2, if2D) # Generate outer bounds for KDE
  dims <- 3
  if(if2D) { dims <- 2 }
  fhat1 <- kde(data1, H=band1, xmin=bounds[1:dims], xmax=bounds[(dims+1):(dims*2)])
  if(typeof(fhat1$x) == "list") { fhat1$x  <- data.matrix(fhat1$x) }
  fhat2 <- kde(data2, H=band2, xmin=bounds[1:dims], xmax=bounds[(dims+1):(dims*2)])
  if(typeof(fhat2$x) == "list") { fhat2$x  <- data.matrix(fhat2$x) }
  # handle 3D
  if(!if2D) {
    imgName <- paste(imgDir,"/",genLabel(m,n,pilot),".html",sep="")
    plot(fhat1, display="rgl", cont=percs, asp=1, col=colorDouble1, alpha=opacityDouble1)
    plot(fhat2, display="rgl", cont=percs, asp=1, add=TRUE, col=colorDouble2, alpha=opacityDouble2)
    scene <- scene3d()
    saveWidget(rglwidget(scene), file=imgName)
    rgl.close() }
  # handle 2D
  else{
    imgName <- paste(imgDir, "/", genLabel(m,n,pilot), ".png", sep="")
    png(imgName)
    plot(fhat1, display=display2D, cont=percs, asp=1, col=colorDouble1, alpha=0.5)
    plot(fhat2, display=display2D, cont=percs, asp=1, add=TRUE, col=colorDouble2, alpha=0.5)
    dev.off()
  }
  vols <- vector()
  for(perc in percs) {
    vols <- append(vols, calcKernelVol(fhat1, perc))
    vols <- append(vols, calcKernelVol(fhat2, perc))
    vols <- append(vols, calcIntersect(fhat1, fhat2, perc)) }
  return(vols) }

KDESingle <- function(data, if2D, percs, ms, ns, pilots, imgDir, colorSingle, opacitySingle, display2D) { # Performs KDE for single volume with all combinations of settings
  volumes <- data.frame(matrix(ncol=1+length(percs), nrow=0))
  colnames(volumes) <- c("Label", paste(percs))
  for(m in ms) { # Iterate through options for bandwidth optimization/selection
    for(n in ns) {
      for(pilot in pilots) {
        vols <- KDETrialSingle(data, if2D, percs, m, n, pilot, imgDir, colorSingle, opacitySingle, display2D)
        row <- data.frame(c(genLabel(m,n,pilot), as.list(vols))) # Construct row for output matrix
        colnames(row) <- c("Label", paste(percs)) # Rename columns for merging
        volumes <- rbind(volumes, row) }}}
  return(volumes) }

KDEDouble <- function(data1, data2, if2D, percs, ms, ns, pilots, imgDir, colorDouble1, colorDouble2, opacityDouble1, opacityDouble2, display2D) { # Performs KDE for two volumes with all combinations of settings
  volumes <- data.frame(matrix(ncol=1+3*length(percs), nrow=0))
  prefixes <- c("V1", "V2", "V&")
  volnames <- c(outer(prefixes, paste(percs), paste))
  colnames(volumes) <- c("Label", volnames)
  for(m in ms) {
    for(n in ns) {
      for(pilot in pilots) {
        vols <- KDETrialDouble(data1, data2, if2D, percs, m, n, pilot, imgDir, colorDouble1, colorDouble2, opacityDouble1, opacityDouble2, display2D)
        row <- data.frame(c(genLabel(m,n,pilot), as.list(vols)))
        colnames(row) <- c("Label", volnames)
        volumes <- rbind(volumes, row) }}}
  return(volumes) }

prepData <- function(raw, name, nameCol, xCol, yCol, zCol, zIncr, ifNoise, if2D) { # Transforms the data into a usable form
  data <- raw[raw[nameCol] == name,] # Select only rows corresponding to desired animal
  if(if2D) {
    data <- select(data, xCol, yCol)
    colnames(data) <- c("X", "Y") }
  else {
    data <- select(data, xCol, yCol, zCol) # Select coordinate columns as X,Y,Z
    colnames(data) <- c("X", "Y", "Z") } # Rename columns to X,Y,Z
  data <- na.omit(data) # Remove rows with missing data
  # Adding noise here. runif(n, min, max) produces a uniform sample of size n between the values of min and max
  if(ifNoise & !if2D) { data[,3] <- data[,3] + runif(nrow(data), -zIncr, 0) } # Add noise to Z
  return(data) }

run <- function(path, sheet, nameCol, xCol, yCol, zCol, dir, out_file, excluded, zIncr, ifNoise, ifSingle, ifDouble, if2D, percs, ms, ns, pilots, colorSingle, colorDouble1, colorDouble2, opacitySingle, opacityDouble1, opacityDouble2, display2D) { # Runs program
  raw <- read_excel(path, sheet=sheet)
  names <- unique(raw[nameCol]) # Get unique names for iterating
  colnames(excluded) <- nameCol # Rename columns for processing
  names <- anti_join(names, excluded, by=nameCol) # Remove excluded from names
  if(! dir.exists(dir)) { dir.create(dir) }
  if(if2D) { colorSingle <- c("white", colorSingle) } # Add background color for 2D plots
  if(ifSingle) {
    for(i in 1:nrow(names)) {
      name <- as.character(names[i,])
      data <- prepData(raw, name, nameCol, xCol, yCol, zCol, zIncr, ifNoise, if2D) # Preprocess data
      imgDir <- paste(dir,"/",name,sep="")
      if(! dir.exists(imgDir)) { dir.create(imgDir) }
      volumes <- KDESingle(data, if2D, percs, ms, ns, pilots, imgDir, colorSingle, opacitySingle, display2D) # Perform calculations
      print(paste(name,":",sep="")) # Output results
      print(volumes)
      out_file_name = paste(dir, (paste(name, "output.csv", sep="-")), sep="\\")
      write.table(volumes, out_file_name, row.names=TRUE, sep=", ", col.names=TRUE, quote=TRUE, na="NA")
      }}
  if(nrow(names) > 1 & ifDouble) {
    for(i in 1:(nrow(names)-1)) {
      name1 <- as.character(names[i,])
      data1 <- prepData(raw, name1, nameCol, xCol, yCol, zCol, zIncr, ifNoise, if2D)
      for(j in (i+1):nrow(names)) {
        name2 <- as.character(names[j,])
        data2 <- prepData(raw, name2, nameCol, xCol, yCol, zCol, zIncr, ifNoise, if2D)
        tag <- paste(name1,"&",name2)
        imgDir <- paste(dir,"/",tag,sep="")
        if(! dir.exists(imgDir)) { dir.create(imgDir) }
        volumes <- KDEDouble(data1, data2, if2D, percs, ms, ns, pilots, imgDir, colorDouble1, colorDouble2, opacityDouble1, opacityDouble2, display2D)
        print(paste(tag,":",sep=""))
        print(volumes)
        out_file_name = paste(dir, (paste(name1, name2, "output.csv", sep="-")), sep="\\")
        write.table(volumes, out_file_name, row.names=TRUE, sep=", ", col.names=TRUE, quote=TRUE, na="NA")
        }}}}


## Data Parameters

# args[1] is the JSON path
args = commandArgs(trailingOnly=TRUE)
print(args)

#Use the next line to hardcode path if line below it is causing problems
# params <- fromJSON(file="C:/Users/Kevin/Documents/Git/Zoo-Mapper/kde_args.json")
params <- fromJSON(file = args[1])

# path <- "C:/Users/Kevin/Documents/CISC498/Sample Data for 3D Distances.xlsx"        # Path of data
 sheet <- 1                                                            # Sheet number (starts at 1) 

## Processing Parameters
# OUTPUT NOW COMES FROM PYTHON CALL
# args = commandArgs(trailingOnly=TRUE)            
dir <- params$output_dir
out_file <- paste(dir, "output.csv", sep="\\")                                     # Output directory
# out_file <- paste(dir, "/output.csv")
# dir <- file.choose()
excluded <- data.frame(c("Calibration"))                              # Names to be excluded
#zIncr <- 5.18134715 - 3.454231434                                     # Increment in Z for adding noise
ifNoise <- TRUE                                                      # Controls if there is noise added
ifSingle <- TRUE                                                      # Controls if the single-entity KDEs are done
ifDouble <- TRUE                                                      # Controls if the double-entity KDEs are done

## Display Parameters                                                 # Lengths should match length of percs
colorSingle <- c("red", "black")                                      # Colors for single-entity KDEs
colorDouble1 <- c("yellow", "red")                                     # Colors for first entity of 3D double-entity KDEs
colorDouble2 <- c("pink", "cyan")                                     # Colors for second entity of 3D double-entity KDEs
opacitySingle <- c(0.35, 1)                                           # Opacities for 3D single-entity KDEs
opacityDouble1 <- c(0.25, 0.50, 0.95)                                       # Opacities for first entity of 3D double-entity KDEs
opacityDouble2 <- c(0.25, 0.50, 0.95)                                       # Opacities for second entity of 3D double-entity KDEs
display2D <- "filled.contour"                                         # Plot type for 2D (filled.contour, slice, persp, image)

#moved args assignment to assignment or DIR for the python menu implementation
#args = commandArgs(trailingOnly=TRUE)

# Set static args
path <- params$filename
if2D <- params$is2d
nameCol <- params$name_col
xCol <- params$x_col
yCol <- params$y_col
zCol <- params$z_col
ifNoise <- params$noise
ms <- params$m
ns <- params$n
samse <- params$samse
unconstr <- params$unconstr
dscalar <- params$dscalar
dunconstr <- params$dunconstr
enclosure_depth <- as.integer(params$enclosure_depth)
depth_sections <- as.integer(params$depth_sections)

# Set contours (percs)
percs <- params$cs

# Determining depth section height
# Currently, heights are marked as the top of a section, so the range between the max and min
# depth values goes from the top of the highest section to the top of the lowest section.
# The range of the bottom section is not included, so we subtract 1 from section count
# when finding heights of individual sections below

zIncr <- enclosure_depth / depth_sections


pilots <- c()
if(samse){
  pilots <- c(pilots, "samse")
}
if(unconstr){
  pilots <- c(pilots, "unconstr")
}
if(dscalar){
  pilots <- c(pilots, "dscalar")
}
if(dunconstr){
  pilots <- c(pilots, "dunconstr")
}

# Run Program
run(path, sheet, nameCol, xCol, yCol, zCol, dir, out_file, excluded, zIncr, ifNoise, ifSingle, ifDouble, if2D, percs, ms, ns, pilots, colorSingle, colorDouble1, colorDouble2, opacitySingle, opacityDouble1, opacityDouble2, display2D)
