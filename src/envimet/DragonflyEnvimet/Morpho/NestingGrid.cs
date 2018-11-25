using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;
using envimetGrid;

namespace Morpho
{
    public class NestingGrid : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public NestingGrid()
          : base("DF Envimet Nesting Grid", "DFEnvimetNestingGrid",
              "Use this component to generate inputs for \"Dragonfly Envimet Spaces\"",
              "Dragonfly", "3 | Envimet")
        {
            this.Message = "VER 0.0.03\nNOV_26_2018";
        }

        public override GH_Exposure Exposure => GH_Exposure.primary;

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddIntegerParameter("numNestingGrid_", "numNestingGrid_", "Connect an integer to set how many nesting cells to use for calculation. Default value is 3.", GH_ParamAccess.item, 3);
            pManager.AddTextParameter("soilProfileA_", "soilProfileA_", "Connect a profileId that you want to use as first material of nesting grid. If no id is provided it will be 'LO'.", GH_ParamAccess.item, "0000LO");
            pManager.AddTextParameter("soilProfileB_", "soilProfileB_", "Connect a profileId that you want to use as second material of nesting grid. If no id is provided it will be 'LO'.", GH_ParamAccess.item, "0000LO");
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("nestingGrid", "nestingGrid", "Connect this output to \"Dragonfly Envimet Spaces\" in order to change nesting grid data in ENVI-Met model.", GH_ParamAccess.item);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // INPUT
            // declaration
            int numNestingGrid_ = 3;
            string soilProfileA_ = "0000LO";
            string soilProfileB_ = "0000LO";

            DA.GetData(0, ref numNestingGrid_);
            DA.GetData(1, ref soilProfileA_);
            DA.GetData(2, ref soilProfileB_);

            // actions
            envimetGrid.NestingGrid nGrid = new envimetGrid.NestingGrid();

            if (numNestingGrid_ != 0)
                nGrid.NumNestingGrid = numNestingGrid_;
            if (soilProfileA_ != null)
                nGrid.SoilProfileA = soilProfileA_;
            if (soilProfileB_ != null)
                nGrid.SoilProfileB = soilProfileB_;

            // OUTPUT
            DA.SetData(0, nGrid);
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
                return DragonflyEnvimet.Properties.Resources.envimetNestingGridIcon;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("5dfe8008-33dc-4f9c-8b63-977d1034a913"); }
        }
    }
}