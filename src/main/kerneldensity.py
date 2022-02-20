import arcpy
from arcpy import env
import xlrd
import argparse
import time
import os
from arcpy.sa import *


def parse_params():
    parser = argparse.ArgumentParser()
    parser.add_argument("--w", type=str, default="D:/data", help="the workspace of arcpy")
    parser.add_argument("--e", type=str, default=r'D:\data\Sample Data for 2D Distances.xlsx',
                        help="the excel path")
    parser.add_argument("--x", type=int, default=17, help="the index of x col")
    parser.add_argument("--y", type=int, default=18, help="the index of y col")
    parser.add_argument("--i", type=int, default=0, help="the sheet index [0,1,2,...]")
    parser.add_argument("--s", type=int, default=1, help="index of the start row")
    parser.add_argument("--p", type=float, default=0.5, help="percent of the range[0.95,0.50]")
    args = parser.parse_args()
    create_shp(args.w, args.e, args.x, args.y, args.i, args.s, args.p)


def create_shp(w, e, x, y, i, s, p):
    env.workspace = w
    excel_path = e
    excel = xlrd.open_workbook(excel_path)
    table = excel.sheet_by_index(i)
    row_count = table.nrows
    col_x = x
    col_y = y
    pointList = []
    for i in range(s, row_count):
        x = table.cell_value(i, col_x)
        y = table.cell_value(i, col_y)
        pointList.append([x, y])
    point = arcpy.Point()
    pointGeometryList = []
    for pt in pointList:
        point.X = pt[0]
        point.Y = pt[1]
        pointGeometry = arcpy.PointGeometry(point)
        pointGeometryList.append(pointGeometry)
    arcpy.CopyFeatures_management(pointGeometryList, "points" + time.strftime("%M%S", time.localtime()))
    kernel_name = "kernel" + time.strftime("%M%S", time.localtime())
    arcpy.CheckOutExtension("Spatial")
    outKernelDensity = KernelDensity(pointGeometryList, "NONE")
    outKernelDensity.save(kernel_name)
    maxvalue = float(str(arcpy.GetRasterProperties_management(kernel_name, 'MAXIMUM')))
    minvalue = maxvalue * p

    outReclass1 = Reclassify(kernel_name, "Value",
                             RemapRange([[minvalue, maxvalue, 1]]), "NODATA")

    kernel_name2 = "kernel2" + time.strftime("%M%S", time.localtime())
    outReclass1.save(kernel_name2)


if __name__ == '__main__':
    # parse_params()
    print 'you are using this tool to calculate the kernel density,please input the info follow the guides '
    w = input('please input the workspace of arcpy:\n')
    e = input('please input the excel path:\n')
    x = input('please input the index of x col:\n')
    y = input('please input the the index of y col:\n')
    i = input('please input the sheet index [0,1,2,...]:\n')
    s = input('please input the index of the start row:\n')
    p = input('please input the percent of the range[0.95,0.50]:\n')
    print 'start...'
    create_shp(w, e, x, y, i, s, p)
    input('finished ,please input any key to close this panel')
