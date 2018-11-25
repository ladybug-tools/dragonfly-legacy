using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;
using envimetGrid;

namespace Morpho
{
    public class Soil : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public Soil()
          : base("DF Envimet Soil", "DFEnvimetSoil",
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
            pManager.AddBrepParameter("_soil", "_soil", "Geometry that represent ENVI-Met soil.  Geometry must be a Surface or Brep on xy plane.", GH_ParamAccess.list);
            pManager.AddTextParameter("_profileId_", "_profileId_", "ENVI-Met profile id. You can use \"id outputs\" which comes from \"LB ENVI - Met Read Library\"\nDefault is 000000.", GH_ParamAccess.list, "000000");
            pManager.AddTextParameter("baseSoilmaterial_", "baseSoilmaterial_", "ENVI-Met plant id. You can use \"id outputs\" which comes from \"LB ENVI - Met Read Library\".\nDefault is 000000.", GH_ParamAccess.item, "000000");
            pManager[0].Optional = true;
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("envimetSoils", "envimetSoils", "Connect this output to \"Dragonfly Envimet Spaces\" in order to add soils to ENVI-Met model.", GH_ParamAccess.item);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // INPUT
            // declaration
            List<Brep> _soil = new List<Brep>();
            List<string> _profileId_ = new List<string>();
            string baseSoilmaterial_ = null;

            DA.GetDataList<Brep>(0, _soil);
            DA.GetDataList<string>(1, _profileId_);
            DA.GetData(2, ref baseSoilmaterial_);

            // actions
            envimetGrid.Element2dMatrix soil = new envimetGrid.Element2dMatrix(baseSoilmaterial_, _profileId_, _soil);

            // OUTPUT
            DA.SetData(0, soil);
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
                return DragonflyEnvimet.Properties.Resources.envimetSoilIcon;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("5e4bd791-9662-45d6-b224-523dac22a068"); }
        }
    }
}