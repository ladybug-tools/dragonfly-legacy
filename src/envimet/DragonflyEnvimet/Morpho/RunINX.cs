using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;
using System.Diagnostics;
namespace DragonflyEnvimet
{
    public class RunINX : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public RunINX()
          : base("DF Envimet Run INX", "DFEnvimetRunINX",
              "Use this component to open your ENVI_MET model directly with GH.",
              "Dragonfly", "3 | Envimet")
        {
            this.Message = "VER 0.0.03\nNOV_26_2018";
        }

        public override GH_Exposure Exposure => GH_Exposure.quarternary;

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("_INXfileAddress", "_INXfileAddress", "Connect the output of DF Envimet Spaces.", GH_ParamAccess.item);
            pManager.AddBooleanParameter("_runIt", "_runIt", "Set runIt to \"True\" to run model.", GH_ParamAccess.item, false);
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // INPUT
            // declaration
            string _INXfileAddress = String.Empty;
            bool _runIt = false;

            DA.GetData(0, ref _INXfileAddress);
            DA.GetData(1, ref _runIt);

            // exe
            if (_runIt)
                Process.Start(_INXfileAddress);
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
                return DragonflyEnvimet.Properties.Resources.envimetRunINXIcon;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("d6a2d00a-fff1-442e-bc1f-9429bd72811a"); }
        }
    }
}