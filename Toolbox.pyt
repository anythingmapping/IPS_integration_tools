

import arcpy
import datetime
import os
import sys


# ============================== process notes =========================
###################################
####### DELIVERY - ACT I ##########
###################################
# Fill in Metrics section
# DOWNLOAD DWG FROM VAULT
# PROJECT USING special loader script
# complete the pricing algorithm
# copy the template in IPS/templates
# fix the geometry of the cad mains before moving to scratch
# manually copy lines to scratch


###################################
####### THE UPDATE - ACT II #######
###################################
# assets need to know their type first -
# so start with mains and manually complete diameter and subtype because this decides so much
#
# SNAP GEOPROCESSING TOOL IN PRO
#arcpy.edit.Snap("waterFixtures", "waterMains VERTEX '0.2 Unknown'")
#arcpy.edit.Snap("waterFixtures", "waterServices END '0.2 Unknown'")
#arcpy.edit.Snap("waterServices", "waterMains EDGE '0.2 Unknown'")


###################################
####### THE INTEGRATION - ACT III ###
###################################
#load the template so you can see it but do not copy yet
#SPLITS & NODE CREATION
#copy features
#now continue with making features perfect


#TODO
#


################################################################################
# ================================ pricing algorithm ===========================
################################################################################
split = 2
nd = 8

de = 0
swab = 1
gtvl = 0
slvl = 0
fh = 5

mn100 = 3
mn50 = 1
mani = 17
serviceLines = 17


################################ project settings ####################################
rdufi = "H021"
rdufi = "E015"

roadName = "Heatley Ave"
roadName = "ERIN"

asBuiltNumber = 5385
asBuiltType = "water"

# DATE SETTING
date_fmt = '%d/%m/%Y'
#dateCreatedObj = datetime.date(2016, 10, 25) #date the gis user created the object
dateCreatedObj = datetime.date.today()
dateCreated = datetime.datetime.strftime(dateCreatedObj, date_fmt) #FORMATTED FOR IPS

dateAsBuiltObj =  datetime.date(2016, 7, 1) #moved to top only her for ref
dateAsBuilt = datetime.datetime.strftime(dateAsBuiltObj, date_fmt) #FORMATTED FOR IPS

###########################################
########### HARD CODED SETTINGS ###########
###########################################
USER = 'mostynl'
OWNER = "WATR"
POWNER = "Private"


SDE_CONNECTION = r"C:\Users\mostynl\AppData\Roaming\ESRI\Desktop10.4\ArcCatalog\SQLGISDEV - LM - SDE_DATA.sde"
UNITID_LOOKUP = "SDE_DATA.SDEAdmin.PNCC_HANSEN_NEXT_UNITID"
SDE_IPS_LOOKUP = SDE_CONNECTION + "\\" + UNITID_LOOKUP


################ IGNOR FOR SETUP ######################
#unknown
availableCodes = {'WABF':'WATER BACKFLOW PREVENTERS',
                'WAPS': 'WATER BORES AND PUMP STATIONS',
                'WAFT': 'WATER FIRE FIGHTING TANK',
                'WAHY': 'WATER HYDRANTS',
                'WAMN': 'WATER MAINS',
                'WAMT': 'WATER METERS',
                'WANO': 'WATER NO VALUATION',
                'WASL': 'WATER SERVICE LINES',
                'WASW': 'WATER SWAB LAUNCHERS',
                'WATO': 'WATER TOBIES',
                'WAVL': 'WATER VALVES'}

Water = {'Main': 41,
        'Hydrant': 12,
        'Node': 43,
        'S/Line': 45,
        'Valve': 46,
        'Misc': 70,
        'Toby': 42,
        'Pump': 44,
        'Back Flow':38}





class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Automating AsBuilt's"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [Load, Geometric, CalculateDiameter, CalculateAddress, CalculateAngle, CalculatePnt, CalculateServiceLine, CalculateMainLine, CalculateUnitID]


class Load(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "1. Load Data"
        self.description = ""
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""

        fc = arcpy.Parameter(
            displayName="input dwg",
            name="fc",
            datatype="DECadDrawingDataset",
            parameterType="Required",
            direction="Input")

        params = [fc]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        dwgFile = parameters[0].valueAsText
        baseDir = os.path.dirname(sys.path[0])

        dwgToGdbFolder = baseDir+"\\dwgGdb"
        dwgToGdbFile = "temp"+str(asBuiltNumber)+".gdb"

        dwgToGdb = baseDir+"\\dwgGdb\\"+"temp"+str(asBuiltNumber)+".gdb"
        dwgFileNameSaveFriendly = "CAD"+str(asBuiltNumber)
        polyInput = dwgToGdb + "\\Polyline"
        polyExtract = baseDir + "\\shpAsBuilt\\" + "shp" + dwgFileNameSaveFriendly

        arcpy.CreateFileGDB_management(dwgToGdbFolder, dwgToGdbFile)

        arcpy.conversion.CADToGeodatabase(dwgFile,
            dwgToGdb,
            dwgFileNameSaveFriendly,
            1000,
            "PROJCS['NZGD_2000_Wanganui_Circuit',GEOGCS['GCS_NZGD_2000',DATUM['D_NZGD_2000',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',800000.0],PARAMETER['Central_Meridian',175.4880555555556],PARAMETER['Scale_Factor',1.0],PARAMETER['Latitude_Of_Origin',-40.24194444444444],UNIT['Meter',1.0]];-5223200 -4745700 450265407.001579;-1073.7418235 4194304001953.12;-100000 10000;0.001;0.001;0.001;IsHighPrecision")

        arcpy.Project_management(in_dataset=polyInput,
            out_dataset=polyExtract,
            out_coor_system="PROJCS['NZGD_2000_New_Zealand_Transverse_Mercator',GEOGCS['GCS_NZGD_2000',DATUM['D_NZGD_2000',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',1600000.0],PARAMETER['False_Northing',10000000.0],PARAMETER['Central_Meridian',173.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]", transform_method="", in_coor_system="PROJCS['NZGD_2000_Wanganui_Circuit',GEOGCS['GCS_NZGD_2000',DATUM['D_NZGD_2000',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',800000.0],PARAMETER['Central_Meridian',175.4880555555556],PARAMETER['Scale_Factor',1.0],PARAMETER['Latitude_Of_Origin',-40.24194444444444],UNIT['Meter',1.0]]", preserve_shape="NO_PRESERVE_SHAPE", max_deviation="", vertical="NO_VERTICAL")

        messages.addMessage("############## 1. Loaded Data #############")
        return

class Geometric(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2. Geometric Tool"
        self.description = ""
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""


        params = None
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""


        #arcpy.edit.Snap("waterFixtures", "waterMains VERTEX '0.2 Unknown'")

        arcpy.edit.Snap("waterServices", "waterMains EDGE '0.2 Meters'")
        arcpy.edit.Snap("waterFixtures", "waterMains EDGE '0.2 Meters'")
        arcpy.edit.Snap("waterFixtures", "waterServices END '0.2 Meters'")

        messages.addMessage("############## 2. Snapped Network #############")
        return


class CalculateDiameter(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Calculate Diameter"
        self.description = ""
        self.canRunInBackground = True
        self.category = "test"

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = None
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        messages.addMessage("############## calculated diameter #############")
        return


class CalculateAngle(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Calculate Angle"
        self.description = ""
        self.canRunInBackground = True
        self.category = "test"

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = None
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def helloWorld(self):
        return 1


    def execute(self, parameters, messages):
        """The source code of the tool."""
        a = self.helloWorld()

        messages.addMessage(a)
        return

class CalculateServiceLine(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "4. Calculate Service Line"
        self.description = ""
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""

        fc = arcpy.Parameter(
            displayName="only input main lines",
            name="fc",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        params = [fc]
        return params


    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        fc = parameters[0].valueAsText
        #https://arcpy.wordpress.com/2012/07/12/getting-arcpy-da-rows-back-as-dictionaries/

        flds = ['OBJECTID',\
                'SHAPE',\
                'SERVEROID',\
                'ENABLED',\
                'DATE_CREATED',\
                'USER_CREATED',\
                'DATE_MODIFIED',\
                'USER_MODIFIED',\
                'RDUFI',\
                'HOUSE_NUMBER',\
                'COMPTYPE',\
                'COMPKEY',\
                'UNITID',\
                'OWNER',\
                'DIAMETER',\
                'MATERIAL',\
                'INSTALL_YEAR',\
                'OFFSET',\
                'ASBLT',\
                'SOURCE',\
                'COMMENT',\
                'LENGTH',\
                'UNITTYPE',\
                'SHAPE_Length']


        ############### THE BIG UPDATE ######################
        with arcpy.da.UpdateCursor(fc, flds) as cursor:
            for row in cursor:
                ####### EACH FEAT ###########
                #OBJECTID
                #SHAPE
                row[2] = 0 #2 SERVEROID
                row[3] = 1 #3 ENABLED
                row[4] = dateCreated #4 DATE_CREATED
                row[5] = USER #5 USER_CREATED
                #6 DATE_MODIFIED
                #7 USER_MODIFIED
                row[8] = rdufi #8 RDUFI
                #9HOUSE_NUMBER
                row[10] = 45 #10COMPTYPE
                #11COMPKEY
                #12UNITID
                row[13] = OWNER #13OWNER
                row[14] = 20 #14DIAMETER
                row[15] = "MDPE" #15MATERIAL
                row[16] = dateAsBuilt #16INSTALL_YEAR
                #17OFFSET
                #18ASBLT
                #19SOURCE
                row[18] = asBuiltNumber #18 'ASBLT'
                row[19] = asBuiltNumber #19 'SOURCE'
                #20COMMENT
                #21 LENGTH
                lenNum = row[23]
                rndLenNum = round(lenNum,2)
                row[21] = rndLenNum
                #21 LENGTH
                row[22] = "WATER" #22UNITTYPE
                #23SHAPE_Length


                ###### END EACH FEAT #############
                cursor.updateRow(row)
        messages.addMessage(rndLenNum)
        messages.addMessage("############## completed GenCal remember that slvl logic and angle need to be fixed for valves #############")
        return

class CalculateMainLine(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "3. Calculate Main Line"
        self.description = ""
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""

        fc = arcpy.Parameter(
            displayName="only input main lines",
            name="fc",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        params = [fc]
        return params


    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        fc = parameters[0].valueAsText
        #https://arcpy.wordpress.com/2012/07/12/getting-arcpy-da-rows-back-as-dictionaries/

        flds = ['OBJECTID',\
                'SHAPE',\
                'SERVEROID',\
                'ENABLED',\
                'DATE_CREATED',\
                'USER_CREATED',\
                'DATE_MODIFIED',\
                'USER_MODIFIED',\
                'RDUFI',\
                'HOUSE_NUMBER',\
                'COMPTYPE',\
                'COMPKEY',\
                'UNITID',\
                'UNITID2',\
                'MAINCOMP1',\
                'MAINCOMP2',\
                'PARLINENO',\
                'OWNER',\
                'DIAMETER',\
                'MATERIAL',\
                'INSTALL_YEAR',\
                'CLASS',\
                'ASBLT',\
                'SOURCE',\
                'SOURCE2',\
                'COMMENT',\
                'LENGTH',\
                'UNITTYPE',\
                'DC_TYPE',\
                'DC_NAME',\
                'SHAPE_Length']



        ############### THE BIG UPDATE ######################
        with arcpy.da.UpdateCursor(fc, flds) as cursor:
            for row in cursor:
                ####### EACH FEAT ###########
                #OBJECTID
                #SHAPE
                row[2] = 0 #2 SERVEROID
                row[3] = 1 #3 ENABLED
                row[4] = dateCreated #4 DATE_CREATED
                row[5] = USER #5 USER_CREATED
                #6 DATE_MODIFIED
                #7 USER_MODIFIED
                row[8] = rdufi #8 RDUFI
                #9HOUSE_NUMBER
                row[10] = 45 #10COMPTYPE
                #11COMPKEY
                #12UNITID
                #13'UNITID2'
                row[14] = 43#14 'MAINCOMP1'
                row[15] = 43#15'MAINCOMP2'
                #16'PARLINENO'
                row[17] = OWNER #17'OWNER'
                #row[18] = 100 #18'DIAMETER'
                row[19] = "MDPE"#19'MATERIAL'
                row[20] = dateAsBuilt #20'INSTALL_YEAR'
                #21'CLASS'
                row[22] = asBuiltNumber #22'ASBLT'
                row[23] = asBuiltNumber #23'SOURCE'
                #24'SOURCE2'
                #25'COMMENT'
                #26'LENGTH'
                lenNum = row[30]
                rndLenNum = round(lenNum,2)
                row[26] = rndLenNum
                #26 LENGTH
                #27'UNITTYPE'
                if row[18] >= 100:
                    row[27] = "NONT"
                elif row[18] <= 75:
                    row[27] = "RIDER"
                else:
                    messages.addMessage("experienced UNITYPE ERR")
                #27'UNITTYPE'
                #28'DC_TYPE'
                #29'DC_NAME'
                #30'SHAPE_Length'
                ###### END EACH FEAT #############
                cursor.updateRow(row)
        messages.addMessage(rndLenNum)
        messages.addMessage("############## completed GenCal remember that slvl logic and angle need to be fixed for valves #############")
        return


class CalculatePnt(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "5. Calculate Fixtures"
        self.description = ""
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""

        fc = arcpy.Parameter(
            displayName="Input Scatch feature",
            name="fc",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        params = [fc]
        return params


    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        fc = parameters[0].valueAsText
        flds = ['OBJECTID', 'SHAPE', 'SERVEROID', 'ENABLED', 'DATE_CREATED', \
            'USER_CREATED', 'DATE_MODIFIED', 'USER_MODIFIED', 'RDUFI', \
            'HOUSE_NUMBER', 'X_COORD', 'Y_COORD', 'ANGLE', 'COMPTYPE',\
            'COMPKEY', 'UNITID', 'OWNER','FIXTURE','INSTALL_YEAR','FIXRL',\
            'LEVSOURCE', 'COOSOURCE', 'ASBLT', 'SOURCE', 'COMMENT', \
            'UNITTYPE', 'DC_TYPE', 'DC_NAME']

        ############### THE BIG UPDATE ######################
        with arcpy.da.UpdateCursor(fc, flds) as cursor:
            for row in cursor:
                ####### EACH FEAT ###########
                #0 'OBJECTID'
                #1 'SHAPE'
                row[2] = 0 #2 'SERVEROID'
                row[3] = 1 #3 'ENABLED'
                row[4] = dateCreated #4 'DATE_CREATED'
                row[5] = USER #5 'USER_CREATED'
                #6 'DATE_MODIFIED'
                #7 'USER_MODIFIED'
                row[8] = rdufi #8 'RDUFI'
                #9 'HOUSE_NUMBER'
                row[10] = row[1][0] #10 'X_COORD'
                row[11] = row[1][1] #11 'Y_COORD'
                #12 ANGLE
                if row[13] == 12:
                    row[12] = 90 #12'ANGLE' #this needs to go to a function
                elif row[13] == 46:
                    row[12] = 999
                else:
                    row[12] = 0
                #12 ANGLE END
                #13 'COMPTYPE'
                #14 'COMPKEY'
                #15 'UNITID'
                row[16] = OWNER #16 'OWNER'
                #17 FIXTURE
                if row[13] == 12:
                    row[17] = "FH"
                elif row[13] == 46: #and row[] == 0
                    row[17] = "GTVL"
                elif row[13] == 70:
                    row[17] = "SWPT"
                elif row[13] == 43:
                    row[17] = "ND"
                elif row[13] == 42:
                    row[17] = "MANI"
                else:
                    messages.addMessage("experienced fixture error")
                #17 FIXTURE END
                row[18] = dateAsBuilt #18 'INSTALL_YEAR'
                #19 'FIXRL' #this might need to be manual
                row[20] = 3 #20 'LEVSOURCE'
                row[21] = 5 #21 'COOSOURCE'
                row[22] = asBuiltNumber #22 'ASBLT'
                row[23] = asBuiltNumber #23 'SOURCE'
                #24 'COMMENT'
                #25 UNITTYPE
                if row[17] == "FH":
                    row[25] = "FH"
                elif row[17] == "GTVL":
                    row[25] = "GTVL"
                elif row[17] == "SLVL":
                    row[25] = "SLVL"
                elif row[17] == "SWPT":
                    row[25] = "SWPT"
                elif row[17] == "ND":
                    row[25] = "ND"
                elif row[17] == "MANI":
                    row[25] = "MANI"
                else:
                    messages.addMessage("experienced UNITYPE ERR")
                #25 UNITTYPE END
                #26 'DC_TYPE'
                #27 'DC_NAME'
                ###### END EACH FEAT #############
                cursor.updateRow(row)
        messages.addMessage("############## completed GenCal remember that slvl logic and angle need to be fixed for valves #############")
        return

class CalculateAddress(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Calculate Address"
        self.description = ""
        self.canRunInBackground = True
        self.category = "specilized tools"

    def getParameterInfo(self):
        """Define parameter definitions"""

        addr = arcpy.Parameter(
            displayName="Input Address Lookup Data",
            name="addr",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        addr.value = "addresses"


        assetFeat = arcpy.Parameter(
            displayName="Input ScatchDB assets",
            name="assetFeat",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")


        field = arcpy.Parameter(
            displayName="Field Name",
            name="fieldName",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        #field.parameterDependencies = [assetFeat.name]
        field.value = "HOUSE_NUMBER"

        params = [addr, assetFeat, field]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        """
        assetFeat = parameters[1]
        if assetFeat.value:
            desc = arcpy.Describe(assetFeat.valueAsText)
            if desc.shapeType == 'Point':
                pass
            elif desc.shapeType == 'Polyline':
                pass
            elif desc.shapeType == 'Polygon':
                pass
        """
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        addr = parameters[0].valueAsText
        assetFeat = parameters[1].valueAsText
        field = parameters[2].valueAsText
        exp = roadName#parameters[3].valueAsText


        shapeType = arcpy.Describe(assetFeat).shapeType


        messages.addMessage("Calculating Nearist Address")
        messages.addMessage(shapeType)


        ################################################################
        #################### ADDRESS GEOMETRY ##########################
        ################################################################
        sql = '''ST_NAME = '{0}' '''.format((exp.upper()))
        fields = ['HOUSENUM','SHAPE@XY']
        streetList = []
        with arcpy.da.SearchCursor(addr, fields, sql) as cursor:
            for row in cursor:
                streetList.append(row)
        messages.addMessage(len(streetList))


        ################################################################
        ##################### FEATURE LOOKUP MATH ######################
        ################################################################
        fields = ['COMPTYPE','HOUSE_NUMBER','SHAPE@XY']
        with arcpy.da.UpdateCursor(assetFeat, fields) as cursor:
            messages.addMessage(sql)
            for row in cursor:
                pntFeatX = int(row[2][0])
                pntFeatY = int(row[2][1])
                closestAddress = None
                featDistMin = 500
                for pntAddr in streetList:
                    pntAddrX = int(pntAddr[1][0])
                    pntAddrY = int(pntAddr[1][1])
                    pntDist = math.hypot((pntFeatX-pntAddrX),(pntFeatY-pntAddrY))
                    if pntDist <= featDistMin:
                        featDistMin = pntDist
                        closestAddress = str(pntAddr[0])
                    else:
                        pass
                messages.addMessage(type(closestAddress))
                row[1] = (closestAddress.strip())
                cursor.updateRow(row)
        return


class CalculateUnitID(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "7. Calculate UnitID"
        self.description = ""
        self.canRunInBackground = True


    def getParameterInfo(self):
        """Define parameter definitions"""

        fc = arcpy.Parameter(
            displayName="input features",
            name="fc",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        params = [fc]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        nextUnitId = 0
        fc = parameters[0].valueAsText
        #search for unitID

        with arcpy.da.UpdateCursor(fc,'UNITID') as cursor:
            #every asset selected
            for row in cursor:
                ################################
                with arcpy.da.SearchCursor(SDE_IPS_LOOKUP, ['ASSET','UNITID']) as searchCursor:
                    for searchRow in searchCursor:
                        nextUnitId = searchRow[1]
                #################################
                row[0] = nextUnitId
                cursor.updateRow(row)

            messages.addMessage("completed search unitid")


        #update feature
        #with arcpy.da.UpdateCursor(fc, 'UNITID') as cursor:
        #    for row in cursor:
        #        row[0] = nextUnitId

        #if it works, update the unitID next
        return

