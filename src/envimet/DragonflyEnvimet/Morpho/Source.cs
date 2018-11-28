using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;
using envimetGrid;

namespace Morpho
{
    public class Source : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public Source()
          : base("DF Envimet Source", "DFEnvimetSource",
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
            pManager.AddBrepParameter("_source", "_source", "Geometry that represent ENVI-Met source.  Geometry must be a Surface or Brep on xy plane.", GH_ParamAccess.list);
            pManager.AddTextParameter("_sourceId_", "_sourceId_", "ENVI-Met source id. You can use \"id outputs\" which comes from \"LB ENVI - Met Read Library\".\nDefault is 0000FT.", GH_ParamAccess.list, "0000FT");
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("envimetSources", "envimetSources", "Connect this output to \"Dragonfly Envimet Spaces\" in order to add source to ENVI-Met model.", GH_ParamAccess.item);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // INPUT
            // declaration
            List<Brep> _source = new List<Brep>();
            List<string> _sourceId_ = new List<string>();

            DA.GetDataList<Brep>(0, _source);
            DA.GetDataList<string>(1, _sourceId_);

            // actions
            envimetGrid.Element2dMatrix sources = new envimetGrid.Element2dMatrix("", _sourceId_, _source);

            // OUTPUT
            DA.SetData(0, sources);
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
                return DragonflyEnvimet.Properties.Resources.envimetSourceIcon;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("0c61b2d6-b268-4a77-9d23-a8e90a9dd509"); }
        }
    }
}