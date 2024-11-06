

import os
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Execution.UtilityRunner import UtilityRunner
from PyFoam.Execution.BasicRunner import BasicRunner



# Simulation parameters
tank_diameter = 0.724  # meters
tank_height = 0.724    # meters
fluid_density = 1000   # kg/m³ (typical for water)
fluid_viscosity = 0.001  # Pa·s (water at room temperature)
rotational_speed_rpm = 200  # RPM
impeller_diameter = 0.3  # meters (example value)


from math import pi

rotational_speed_rev_s = rotational_speed_rpm / 60.0  # rev/s
rotational_speed_rad_s = rotational_speed_rev_s * 2 * pi  # rad/s

case_dir = "mixingSimulation"
if not os.path.exists(case_dir):
    os.makedirs(case_dir)



blockMeshDict_content = f"""
FoamFile
{{
    version 2.0;
    format ascii;
    class dictionary;
    object blockMeshDict;
}}

// Geometry parameters
convertToMeters 1.0;

vertices
(
    (0 0 0)
    ({tank_diameter} 0 0)
    ({tank_diameter} {tank_diameter} 0)
    (0 {tank_diameter} 0)
    (0 0 {tank_height})
    ({tank_diameter} 0 {tank_height})
    ({tank_diameter} {tank_diameter} {tank_height})
    (0 {tank_diameter} {tank_height})
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (20 20 20) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    walls
    {{
        type wall;
        faces
        (
            (0 1 5 4)
            (1 2 6 5)
            (2 3 7 6)
            (3 0 4 7)
        );
    }}
    inlet
    {{
        type patch;
        faces
        (
            (0 1 2 3)
        );
    }}
    outlet
    {{
        type patch;
        faces
        (
            (4 5 6 7)
        );
    }}
);

mergePatchPairs
(
);
"""

with open(os.path.join(case_dir, "system", "blockMeshDict"), "w") as f:
    f.write(blockMeshDict_content)


block_mesh = UtilityRunner(argv=["blockMesh", "-case", case_dir])
block_mesh.start()
block_mesh.wait()




snappyHexMeshDict_content = f"""
FoamFile
{{
    version 2.0;
    format ascii;
    class dictionary;
    object snappyHexMeshDict;
}}

castellatedMesh true;
snap true;
addLayers false;

geometry
{{
    Mixer_1.stl
    {{
        type triSurfaceMesh;
        name Mixer_1;
    }}
}}

castellatedMeshControls
{{
    maxLocalCells 1000000;
    maxGlobalCells 2000000;
    minRefinementCells 0;
    maxLoadUnbalance 0.10;
    nCellsBetweenLevels 2;

    features
    (
    );

    refinementSurfaces
    {{
        Mixer_1
        {{
            level (3 5);
        }}
    }}

    resolveFeatureAngle 30;
    refinementRegions
    {{
    }}

    locationInMesh ({tank_diameter/2} {tank_diameter/2} {tank_height/2});
}}

snapControls
{{
    nSmoothPatch 3;
    tolerance 2.0;
    nSolveIter 30;
    nRelaxIter 5;
}}

addLayersControls
{{
}}

meshQualityControls
{{
    maxNonOrtho 65;
    maxBoundarySkewness 20;
    maxInternalSkewness 4;
    maxConcave 80;
    minVol 1e-13;
    minTetQuality 1e-9;
    minArea -1;
    minTwist 0.02;
    minDeterminant 0.001;
    minFaceWeight 0.02;
    minVolRatio 0.01;
    minTriangleTwist -1;
    nSmoothScale 4;
    errorReduction 0.75;
}}

"""

with open(os.path.join(case_dir, "system", "snappyHexMeshDict"), "w") as f:
    f.write(snappyHexMeshDict_content)


snappy_hex_mesh = UtilityRunner(argv=["snappyHexMesh", "-overwrite", "-case", case_dir])
snappy_hex_mesh.start()
snappy_hex_mesh.wait()


transport_properties = ParsedParameterFile(os.path.join(case_dir, "constant", "transportProperties"))
transport_properties["transportModel"] = "Newtonian"
transport_properties["nu"] = fluid_viscosity / fluid_density  # Kinematic viscosity (m²/s)
transport_properties.writeFile()






U = ParsedParameterFile(os.path.join(case_dir, "0", "U"))
U.header = foamFileHeader(class_="volVectorField", location="0", object="U")
U["dimensions"] = "[0 1 -1 0 0 0 0]"
U["internalField"] = "uniform (0 0 0)"
U["boundaryField"]["walls"]["type"] = "wall"
U["boundaryField"]["inlet"]["type"] = "zeroGradient"
U["boundaryField"]["outlet"]["type"] = "zeroGradient"
U.writeFile()





MRF_content = f"""
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      MRFProperties;
}}

MRF1
{{
    cellZone    impellerZone;
    active      yes;

    nonRotatingPatches ();

    origin      (0 0 0);
    axis        (0 0 1);
    omega       {rotational_speed_rad_s};
}}
"""

with open(os.path.join(case_dir, "constant", "MRFProperties"), "w") as f:
    f.write(MRF_content)





simple_foam = BasicRunner(argv=["simpleFoam", "-case", case_dir], silent=True, server=False)
simple_foam.start()
simple_foam.wait()


