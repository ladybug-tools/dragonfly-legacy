using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;
using envimetGrid;

namespace Morpho
{
    public class Plant3d : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public Plant3d()
          : base("DF Envimet  3d Plant", "DFEnvimet3dPlant",
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
            pManager.AddBrepParameter("_plant3D", "_plant3D", "Geometry that represent ENVI-Met plant 3d.  Geometry must be a Surface or Brep on xy plane.", GH_ParamAccess.list);
            pManager.AddTextParameter("_plant3Did_", "_plant3Did_", "ENVI-Met plant id. You can use \"id outputs\" which comes from \"LB ENVI - Met Read Library\".\nDefault is PINETREE.", GH_ParamAccess.list);
            pManager[1].Optional = true;
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("envimet3dPlants", "envimet3dPlants", "Connect this output to \"Morpho Spaces\" in order to add 3d plants to ENVI-Met model.", GH_ParamAccess.item);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // INPUT
            // declaration
            List<Brep> _plant3D = new List<Brep>();
            List<string> _plant3Did_ = new List<string>();

            DA.GetDataList<Brep>(0, _plant3D);
            DA.GetDataList<string>(1, _plant3Did_);

            // actions
            envimetGrid.ThreeDimensionalPlants trees = new envimetGrid.ThreeDimensionalPlants("0000C2,.PINETREE", _plant3Did_, _plant3D);

            // OUTPUT
            DA.SetData(0, trees);
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
                return DragonflyEnvimet.Properties.Resources.envimet3dPlantIcon;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("c350b9ba-b231-40b0-af27-2e7d7f00e49d"); }
        }
    }
}