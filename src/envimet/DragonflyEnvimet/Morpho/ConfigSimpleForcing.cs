using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;
using envimetSimulationFile;

namespace DragonflyEnvimet
{
    public class ConfigSimpleForcing : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public ConfigSimpleForcing()
          : base("DF Envimet Config SimpleForcing", "DFenvimetConfigSimpleForcing",
              "This component let you force climate condition of the simulation. You can connect lists of values or data which comes from EPW file.\nUse outputs of DF Envimet Simple Force by EPW.",
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
            pManager.AddNumberParameter("_dryBulbTemperature", "_dryBulbTemperature", "Connect a list of numbers.\nUnit is Kelvin.", GH_ParamAccess.list);
            pManager.AddNumberParameter("_relativeHumidity", "_relativeHumidity", "Connect a list of numbers.\nUnit is %.", GH_ParamAccess.list);
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("simpleForcing", "simpleForcing", "Simple forcing settings of SIMX file. Connect it to DF Enviment Config.", GH_ParamAccess.item);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // INPUT
            // declaration
            List<double> _dryBulbTemperature = new List<double>();
            List<double> _relativeHumidity = new List<double>();

            DA.GetDataList<double>(0, _dryBulbTemperature);
            DA.GetDataList<double>(1, _relativeHumidity);

            // action
            envimetSimulationFile.SampleForcingSettings simpleF = new envimetSimulationFile.SampleForcingSettings(_dryBulbTemperature, _relativeHumidity);

            // OUTPUT
            DA.SetData(0, simpleF);
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
                return DragonflyEnvimet.Properties.Resources.envimetConfigSimpleForcing;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("40111afb-0301-414a-a215-69263538dad5"); }
        }
    }
}