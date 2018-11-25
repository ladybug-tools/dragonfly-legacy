using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;
using envimetGrid;

namespace Morpho
{
    public class Plant2d : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public Plant2d()
          : base("DF Envimet 2d Plant", "DFEnvimet2dPlant",
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
            pManager.AddBrepParameter("_plant2D", "_plant2D", "Geometry that represent ENVI-Met plant 2d.  Geometry must be a Surface or Brep on xy plane.", GH_ParamAccess.list);
            pManager.AddTextParameter("_plantId_", "_plantId_", "ENVI-Met plant id. You can use \"id outputs\" which comes from \"LB ENVI - Met Read Library\".\nDefault is 0000XX.", GH_ParamAccess.list, "0000XX");
            pManager[1].Optional = true;
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("envimet2dPlants", "envimet2dPlants", "Connect this output to \"Dragonfly Envimet Spaces\" in order to add 3d plants to ENVI-Met model.", GH_ParamAccess.item);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // INPUT
            // declaration
            List<Brep> _plant2D = new List<Brep>();
            List<string> _plantId_ = new List<string>();

            DA.GetDataList<Brep>(0, _plant2D);
            DA.GetDataList<string>(1, _plantId_);

            // actions
            envimetGrid.Element2dMatrix trees = new envimetGrid.Element2dMatrix("", _plantId_, _plant2D);

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
                return DragonflyEnvimet.Properties.Resources.envimet2dPlantIcon;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("60c3094c-b8e0-4476-bb03-06c27ffd08e8"); }
        }
    }
}