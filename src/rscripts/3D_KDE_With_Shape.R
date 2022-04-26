#This file is the same as 3D_KDE_2021 except the function KDETrialSingle now contains instructions to convert the kde to a shapefile.
#More functions may need to add these in order for all the KDE's to be converted properly.
#The libraries sp and maptools are needed for this conversion.


# Load Required Libraries
library (ks)
library (rgl)
library (misc3d)
library (readxl)
library (dplyr)
library (htmlwidgets)
library(ggplot2)
library(sp) #NEEDED FOR CONVERT TO SHAPEFILE
library(maptools) #NEEDED FOR CONVERT TO SHAPEFILE
library(raster) #NEEDED FOR CONVERT TO SHAPEFILE


pandoc_path <- Sys.getenv("RSTUDIO_PANDOC")
print("PANDOC PATH BELOW")
print(pandoc_path)
Sys.setenv(RSTUDIO_PANDOC="C:/Program Files/RStudio/bin/pandoc")
#Sys.setenv(RSTUDIO_PANDOC="./pandoc")
#Sys.setenv(RSTUDIO_PANDOC=pandoc_path)

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
  
  #convert kde to shp file
  spkde <- image2grid(list(x = fhat$eval.points[[1]], 
                           y = fhat$eval.points[[2]],
                           z = fhat$estimate))
  
  countour(spkde, add = TRUE)
  
  r <- raster(spkde)
  r.cont <- rasterToContour(r, nlevels = 20)
  
  #shapefile(r.cont, filename= 'shapefilename', overwrite=FALSE)
  
  ## or alternatively
  
  #writeLinesShape(r.cont, "(shapefilename")
  #END CONVERT TO SHAPEFILE
  
  
  
  
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
  if(!if2D) {
    imgName <- paste(imgDir,"/",genLabel(m,n,pilot),".html",sep="")
    plot(fhat1, display="rgl", cont=percs, asp=1, col=colorDouble1, alpha=opacityDouble1)
    plot(fhat2, display="rgl", cont=percs, asp=1, add=TRUE, col=colorDouble2, alpha=opacityDouble2)
    scene <- scene3d()
    saveWidget(rglwidget(scene), file=imgName)
    rgl.close() }
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
        out_file_name = paste(dir, (paste(name, "output.csv", sep="-")), sep="\\")
        write.table(volumes, out_file_name, row.names=TRUE, sep=", ", col.names=TRUE, quote=TRUE, na="NA")
        }}}}

# Set Parameters

## Data Parameters
# path <- "C:/Users/Kevin/Documents/CISC498/Sample Data for 3D Distances.xlsx"        # Path of data
 sheet <- 1                                                            # Sheet number (starts at 1) 
# nameCol <- "Focal_Shar"                                               # Name column
# xCol <- "LongUTM"                                                     # X-coordinate column
# yCol <- "LatUTM"                                                      # Y-coordinate column
# zCol <- "DepthM"                                                      # Z-coordinate column

# Output
#out_file <- "C:/Users/Kevin/Documents/R/output.csv"

## Processing Parameters
#dir <- choose.dir(caption="Choose an output directory")  
# OUTPUT NOW COMES FROM PYTHON CALL
args = commandArgs(trailingOnly=TRUE)            
dir <- toString(args[17])
out_file <- paste(dir, "output.csv", sep="\\")                                     # Output directory
# out_file <- paste(dir, "/output.csv")
# dir <- file.choose()
excluded <- data.frame(c("Calibration"))                              # Names to be excluded
zIncr <- 5.18134715 - 3.454231434                                     # Increment in Z for adding noise
ifNoise <- TRUE                                                      # Controls if there is noise added
ifSingle <- TRUE                                                      # Controls if the single-entity KDEs are done
ifDouble <- TRUE                                                      # Controls if the double-entity KDEs are done
# if2D <- FALSE                                                         # Controls if the analysis is 2D or 3D

## Analysis Parameters
#percs <- c(50, 95, 100)                                                     # Contour percentages
#ms <- c(5)                                                          # Scaling factors for bandwidth
#ns <- c(1)                                                            # Number of stages in bandwidth optimization (1, 2)
#pilots <- c("samse", "unconstr", "dscalar", "dunconstr")              # Strategy for bandwidth optimization (samse, unconstr, dscalar, dunconstr)
# pilots <- c("samse")

## Display Parameters                                                 # Lengths should match length of percs
colorSingle <- c("red", "black")                                      # Colors for single-entity KDEs
colorDouble1 <- c("yellow", "red")                                     # Colors for first entity of 3D double-entity KDEs
colorDouble2 <- c("pink", "cyan")                                     # Colors for second entity of 3D double-entity KDEs
opacitySingle <- c(0.35, 1)                                           # Opacities for 3D single-entity KDEs
opacityDouble1 <- c(0.25, 0.50, 0.95)                                       # Opacities for first entity of 3D double-entity KDEs
opacityDouble2 <- c(0.25, 0.50, 0.95)                                       # Opacities for second entity of 3D double-entity KDEs
display2D <- "filled.contour"                                         # Plot type for 2D (filled.contour, slice, persp, image)

print("IN 3D_KDE_2021")

#moved args assignment to assignment or DIR for the python menu implementation
#args = commandArgs(trailingOnly=TRUE)

path <- toString(args[1])
if2D <- (args[2] == "t")
nameCol <- toString(args[3])
xCol <- toString(args[4])
yCol <- toString(args[5])
zCol <- toString(args[6])
ifNoise <= (args[7] == "t")
ms <- as.integer(args[8])
ns <- as.integer(args[9])
contour_50 <- (args[10]=="t")
contour_95 <- (args[11]=="t")
contour_100 <- (args[12]=="t")
samse <- (args[13]=="t")
unconstr <- (args[14]=="t")
dscalar <- (args[15]=="t")
dunconstr <- (args[16]=="t")

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
print(pilots)

percs <- c()
if(contour_50){
  percs <- c(percs, 50)
}
if(contour_95){
  percs <- c(percs, 95)
}
if(contour_100){
  percs <- c(percs, 100)
}
print(percs)


#path <- ("C:/Users/Kevin/Documents/CISC498/Sample Test Calculations/Mid depth vs top depth 2D and 3D test calculations.xlsx")
#sheet <- 4
#if2D <- FALSE
#nameCol <- "Focal_Shar"
#xCol <- "LongUTM"
#yCol <- "LatUTM"
#zCol <- "DepthMid"

# Run Program
run(path, sheet, nameCol, xCol, yCol, zCol, dir, out_file, excluded, zIncr, ifNoise, ifSingle, ifDouble, if2D, percs, ms, ns, pilots, colorSingle, colorDouble1, colorDouble2, opacitySingle, opacityDouble1, opacityDouble2, display2D)
