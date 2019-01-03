using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;
using System.Xml;
using System.Text;
using System.Linq;
using envimetGrid;
using envimentIntegration;
using envimentManagment;
namespace Morpho
{
    public class Spaces : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public Spaces()
          : base("DF Envimet Spaces", "DFEnvimetSpaces",
              "Use this component to generate ENVI-Met v4.4 3D geometry models.\nAnalyze parametric models with ENVI - Met!\nSave the model in the ENVI_MET Workspace, create a simulation file with \"DF Envimet Config\" and run the simulation.",
              "Dragonfly", "3 | Envimet")
        {
            this.Message = "VER 0.0.03\nNOV_26_2018";
        }

        public override GH_Exposure Exposure => GH_Exposure.tertiary;

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddTextParameter("_envimetFolder", "_envimetFolder", "The folder into which you would like to write the envimet model. This should be a complete file path to the folder.", GH_ParamAccess.item);
            pManager.AddGenericParameter("_envimetLocation", "_envimetLocation", "Location data which comes from \"Dragonfly Envimet Location\" component.", GH_ParamAccess.item);
            pManager.AddGenericParameter("_envimentGrid", "_envimentGrid", "Connect the output of \"Dragonfly Envimet Grid\".", GH_ParamAccess.item);
            pManager.AddGenericParameter("nestingGrid_", "nestingGrid_", "Connect the output of \"Dragonfly Envimet Nesting Grid\".", GH_ParamAccess.item);
            pManager.AddGenericParameter("_envimetBuidings", "_envimetBuidings", "Connect the output of \"Dragonfly Envimet Buildings\".", GH_ParamAccess.item);
            pManager.AddGenericParameter("_envimetSoils", "_envimetSoils", "Connect the output of \"Dragonfly Envimet Soil\".", GH_ParamAccess.item);
            pManager.AddGenericParameter("envimet2dPlants_", "envimet2dPlants_", "Connect the output of \"Dragonfly Envimet 2d Plant\".", GH_ParamAccess.item);
            pManager.AddGenericParameter("envimet3dPlants_", "envimet3dPlants_", "Connect the output of \"Dragonfly Envimet 3d Plant\".", GH_ParamAccess.item);
            pManager.AddGenericParameter("envimetSources_", "envimetSources_", "Connect the output of \"Dragonfly Envimet Source\".", GH_ParamAccess.item);
            pManager.AddTextParameter("fileName_", "fileName_", "The file name that you would like the envimet model to be saved as. Default name is \"DragonflyEnvimet\".", GH_ParamAccess.item, "DragonflyEnvimet");
            pManager.AddBooleanParameter("_runIt", "_runIt", "Set to \"True\" to run the component and generate the envimet model.", GH_ParamAccess.item, false);
            pManager.AddBooleanParameter("viewGridXY_", "viewGridXY_", "Set to \"True\" to run the view XY grid.", GH_ParamAccess.item, false);
            pManager.AddBooleanParameter("viewGridXZ_", "viewGridXZ_", "Set to \"True\" to run the view XZ grid.", GH_ParamAccess.item, false);
            pManager.AddBooleanParameter("viewGridYZ_", "viewGridYZ_", "Set to \"True\" to run the view YZ grid.", GH_ParamAccess.item, false);
            pManager[3].Optional = true;
            pManager[6].Optional = true;
            pManager[7].Optional = true;
            pManager[8].Optional = true;
            pManager[9].Optional = true;
            pManager[11].Optional = true;
            pManager[12].Optional = true;
            pManager[13].Optional = true;
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddPointParameter("XYGrid", "XYGrid", "XY points.", GH_ParamAccess.list);
            pManager.AddPointParameter("XZGrid", "XZGrid", "XZ points.", GH_ParamAccess.list);
            pManager.AddPointParameter("YZGrid", "YZGrid", "YZ points.", GH_ParamAccess.list);
            pManager.AddTextParameter("INXfileAddress", "INXfileAddress", "The file path of the inx result file that has been generated on your machine.", GH_ParamAccess.item);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // INPUT

            // surface
            List<Mesh> baseSurfMesh = new List<Mesh>();

            // building
            List<Mesh> bgeo = new List<Mesh>();
            List<string> wallmat = new List<string>();
            List<string> roofmat = new List<string>();

            List<int> idgreen = new List<int>();
            List<string> greenwallmat = new List<string>();
            List<string> greenroofmat = new List<string>();

            string cwallmat = null;
            string croofomat = null;
            // location
            string loc = "Site:Location,\nunknown_Location,\n0.0, !Latitude\n0.0, !Longitude\n0.0, !Time Zone\n0.0; !Elevation\n";
            int rotation = 0;
            // soil
            string bsoilmat = null;
            List<string> soilmat = new List<string>();
            List<Brep> sgeo = new List<Brep>();
            // folder
            string _envimetFolder = null;
            // plant2d
            string p2ddefmat = null;
            List<string> p2dmat = new List<string>();
            List<Brep> p2dgeo = new List<Brep>();
            // plant3d
            string p3ddefmat = null;
            List<string> p3dmat = new List<string>();
            List<Brep> p3dgeo = new List<Brep>();
            // plant3d
            string srcdefmat = null;
            List<string> srcmat = new List<string>();
            List<Brep> srcgeo = new List<Brep>();
            // filename
            string fileName_ = "Morpho";
            // runit
            bool _runIt = false;
            // view
            bool viewGridXY_ = false;
            bool viewGridXZ_ = false;
            bool viewGridYZ_ = false;
            
            envimentIntegration.LocationFromLB _envimetLocation = new envimentIntegration.LocationFromLB(loc, rotation);
            envimetGrid.AutoGrid _envimentGrid = new envimetGrid.AutoGrid();
            envimetGrid.BuildingMatrix _envimetBuidings = new envimetGrid.BuildingMatrix(bgeo, wallmat, roofmat, cwallmat, croofomat, idgreen, greenwallmat, greenroofmat);
            envimetGrid.Element2dMatrix _envimetSoils = new envimetGrid.Element2dMatrix(bsoilmat, soilmat, sgeo);
            envimetGrid.NestingGrid nestingGrid_ = new envimetGrid.NestingGrid();
            envimetGrid.Element2dMatrix envimet2dPlants_ = new envimetGrid.Element2dMatrix(p2ddefmat, p2dmat, p2dgeo);
            envimetGrid.ThreeDimensionalPlants envimet3dPlants_ = new envimetGrid.ThreeDimensionalPlants(p3ddefmat, p3dmat, p3dgeo);
            envimetGrid.Element2dMatrix envimetSources_ = new envimetGrid.Element2dMatrix(srcdefmat, srcmat, srcgeo);

            DA.GetData(0, ref _envimetFolder);
            DA.GetData(1, ref _envimetLocation);
            DA.GetData(2, ref _envimentGrid);
            DA.GetData(3, ref nestingGrid_);
            DA.GetData(4, ref _envimetBuidings);
            DA.GetData(5, ref _envimetSoils);
            DA.GetData(6, ref envimet2dPlants_);
            DA.GetData(7, ref envimet3dPlants_);
            DA.GetData(8, ref envimetSources_);
            DA.GetData(9, ref fileName_);
            DA.GetData(10, ref _runIt);
            DA.GetData(11, ref viewGridXY_);
            DA.GetData(12, ref viewGridXZ_);
            DA.GetData(13, ref viewGridYZ_);

            // actions
            if (_envimentGrid.Surface == null)
            {
                _envimentGrid.gZmethod(_envimetBuidings.Buildings); // INIT
            }
            else
            {
                baseSurfMesh.Add(_envimentGrid.Surface);
                _envimentGrid.gZmethod(baseSurfMesh); // INIT
            }


            if (viewGridXY_ == true)
            {
                DA.SetDataList(0, _envimentGrid.GridXY());
            }
            if (viewGridXZ_ == true)
            {
                DA.SetDataList(1, _envimentGrid.GridXZ());
            }
            if (viewGridYZ_ == true)
            {
                DA.SetDataList(2, _envimentGrid.GridYZ());
            }

            /// RUNIT

            string fileName = (fileName_ != null) ? fileName_ + ".INX" : "DragonflyEnvimet.INX";
            string fullName = System.IO.Path.Combine(_envimetFolder, fileName);

            if (_runIt == true)
            { 
                envimentManagment.WriteINX.INXwriteMethod(fullName, _envimentGrid, nestingGrid_, _envimetLocation, _envimetBuidings, envimet2dPlants_, _envimetSoils, envimetSources_, envimet3dPlants_);
                DA.SetData(3, fullName);
            }

        }

        /// <summary>
        /// Provides an Icon for the component.
        /// </summary>
        protected override System.Drawing.Bitmap Icon
        {
            get
            {
                //You can add image files to your project resources and access them like this:
                // return Resources.IconForThisComponent;
                return DragonflyEnvimet.Properties.Resources.envimetSpacesIcon;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("f864e5d3-8f31-4d9d-89bb-bb6f25c6c931"); }
        }
    }
}