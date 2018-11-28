using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;
using envimetGrid;

// In order to load the result of this wizard, you will also need to
// add the output bin/ folder of this project to the list of loaded
// folder in Grasshopper.
// You can use the _GrasshopperDeveloperSettings Rhino command for that.

namespace Morpho
{
    public class Buildings : GH_Component
    {
        /// <summary>
        /// Each implementation of GH_Component must provide a public 
        /// constructor without any arguments.
        /// Category represents the Tab in which the component will appear, 
        /// Subcategory the panel. If you use non-existing tab or panel names, 
        /// new tabs/panels will automatically be created.
        /// </summary>
        public Buildings()
          : base("DF Envimet Buildings", "DFEnvimetBuildings",
              "Use this component to generate inputs for \"Dragonfly Envimet Spaces\"",
              "Dragonfly", "3 | Envimet")
        {
            this.Message = "VER 0.0.03\nNOV_26_2018";
        }

        public override GH_Exposure Exposure => GH_Exposure.secondary;

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddMeshParameter("_buildings", "_buildings", "Geometry that represent ENVI-Met buildings.\nGeometries have to be closed Brep or Mesh", GH_ParamAccess.list);
            pManager.AddTextParameter("wallMaterial_", "wallMaterial_", "Use this input to change wall materials.\nMaterials count have to be equals buildings count, otherwise it will be set the default material.", GH_ParamAccess.list, "000000");
            pManager.AddTextParameter("roofMaterial_", "roofMaterial_", "Use this input to change roof materials. Materials count have to be equals buildings count, otherwise it will be set the default material.", GH_ParamAccess.list, "000000");
            pManager.AddTextParameter("commonWallMaterial_", "commonWallMaterial_", "Default wall property. Use this input to set default building materials.\nDefault material is \"00\"", GH_ParamAccess.item, "000000");
            pManager.AddTextParameter("commonRoofMaterial_", "commonRoofMaterial_", "Default roof property. Use this input to set default building materials.\nDefault material is \"00\"", GH_ParamAccess.item, "000000");

            pManager.AddIntegerParameter("greenBuildingsId_", "greenBuildingsId_", "Connect a list of integer which represent the buildings you want to apply greenings materials.", GH_ParamAccess.list);
            pManager.AddTextParameter("greenWallMaterial_", "greenWallMaterial_", "Connect a list of greenings material to apply them to walls of selected buildings.", GH_ParamAccess.list);
            pManager.AddTextParameter("greenRoofMaterial_", "greenRoofMaterial_", "Connect a list of greenings material to apply them to roofs of selected buildings.", GH_ParamAccess.list);
            pManager[5].Optional = true;
            pManager[6].Optional = true;
            pManager[7].Optional = true;
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("envimetBuidings", "envimetBuidings", "Connect this output to \"Dragonfly Envimet Spaces\" in order to add buildings to ENVI-Met model.", GH_ParamAccess.item);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object can be used to retrieve data from input parameters and 
        /// to store data in output parameters.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // INPUT
            // declaration
            List<Mesh> _buildings = new List<Mesh>();
            List<string> wallMaterial_ = new List<string>();
            List<string> roofMaterial_ = new List<string>();

            List<int> greenBuildingsId_ = new List<int>();
            List<string> greenWallMaterial_ = new List<string>();
            List<string> greenRoofMaterial_ = new List<string>();

            string commonWallMaterial_ = null;
            string commonRoofMaterial_ = null;

            DA.GetDataList<Mesh>(0, _buildings);
            DA.GetDataList<string>(1, wallMaterial_);
            DA.GetDataList<string>(2, roofMaterial_);
            DA.GetData(3, ref commonWallMaterial_);
            DA.GetData(4, ref commonRoofMaterial_);

            DA.GetDataList<int>(5, greenBuildingsId_);
            DA.GetDataList<string>(6, greenWallMaterial_);
            DA.GetDataList<string>(7, greenRoofMaterial_);

            // actions
            envimetGrid.BuildingMatrix envimetBuildings = new envimetGrid.BuildingMatrix(_buildings, wallMaterial_, roofMaterial_, commonWallMaterial_, commonRoofMaterial_, greenBuildingsId_, greenWallMaterial_, greenRoofMaterial_);

            foreach (Mesh m in envimetBuildings.Buildings)
            {
                if (!(m.IsClosed))
                {
                    this.AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, "Please provide closed geometries");
                    return;
                }
            }


            // OUTPUT
            //DA.SetData(0, (object)envimetBuildings);
            DA.SetData(0, envimetBuildings);
        }

        /// <summary>
        /// Provides an Icon for every component that will be visible in the User Interface.
        /// Icons need to be 24x24 pixels.
        /// </summary>
        protected override System.Drawing.Bitmap Icon
        {
            get
            {
                // You can add image files to your project resources and access them like this:
                //return Resources.IconForThisComponent;
                return DragonflyEnvimet.Properties.Resources.envimetBuilingIcon;
            }
        }

        /// <summary>
        /// Each component must have a unique Guid to identify it. 
        /// It is vital this Guid doesn't change otherwise old ghx files 
        /// that use the old ID will partially fail during loading.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("83ec6b8d-4fa2-48f1-98d5-369fc9fa6ae5"); }
        }
    }
}
