using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;
using envimetSimulationFile;

namespace DragonflyEnvimet
{
    public class ConfigMainSettings : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public ConfigMainSettings()
          : base("DF Envimet Config MainSettings", "DFenvimetConfigMainSettings",
              "This component contain main settings to generate simulation file (SIMX).\nConnect the output DF Envimet Config.",
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
            pManager.AddTextParameter("simName_", "simName_", "The file name that you would like the sim file to be saved as.", GH_ParamAccess.item, "DragonflyConfig");
            pManager.AddTextParameter("_INXfileAddress", "_INXfileAddress", "The path comes from DF Envimet Spaces.", GH_ParamAccess.item);
            pManager.AddTextParameter("startDate_", "startDate_", "Connect the output of \"DF Envimet Simply Force by EPW\" or a text.\nThe format have to be: DD.MM.YYYY\nDefault value is 21.06.2018", GH_ParamAccess.item, "21.06.2018");
            pManager.AddTextParameter("startTime_", "startTime_", "Connect the output of \"DF Envimet Simply Force by EPW\" or a text.\nThe format have to be: hh:mm:ss\nDefault value is 06:00:00", GH_ParamAccess.item, "06:00:00");

            pManager.AddIntegerParameter("simDuration_", "simDuration_", "Total Simulation Time in Hours.\nDefault value is 24. Usually from 24 to 48 hours.", GH_ParamAccess.item, 24);
            pManager.AddNumberParameter("windSpeed_", "windSpeed_", "Wind Speed in 10 m ab. Ground [m/s]. Default value is 3.0 m/s.", GH_ParamAccess.item, 3.00);
            pManager.AddNumberParameter("windDirection_", "windDirection_", "Wind Direction (0:N..90:E..180:S..270:W..). Default value is 0.", GH_ParamAccess.item, 0.00);
            pManager.AddNumberParameter("roughness_", "roughness_", "Roughness Length z0 at Reference Point [m]. Default value is 0.01.", GH_ParamAccess.item, 0.01);
            pManager.AddNumberParameter("initialTemperature_", "initialTemperature_", "Initial Temperature Atmosphere [°C]. Default value is 21 °C.", GH_ParamAccess.item, 21.00);
            pManager.AddNumberParameter("specificHumidity_", "specificHumidity_", "Specific Humidity in 2500 m [g Water/kg air]. Default value is 7.0.", GH_ParamAccess.item, 7.00);
            pManager.AddNumberParameter("relativeHumidity_", "relativeHumidity_", "Relative Humidity in 2m [%]. Default value is 50%.", GH_ParamAccess.item, 50.00);
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("mainSettings", "mainSettings", "Basic settings of SIMX file. Connect it to DF Enviment Config.", GH_ParamAccess.item);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // INPUT
            // declaration
            string simName_ = null;
            string _INXfileAddress = null;
            string startDate_ = null;
            string startTime_ = null;

            int simDuration_ = 0;
            double windSpeed_ = 0;
            double windDirection_ = 0;
            double roughness_ = 0;
            double initialTemperature_ = 0;
            double specificHumidity_ = 0;
            double relativeHumidity_ = 0;

            DA.GetData(0, ref simName_);
            DA.GetData(1, ref _INXfileAddress);
            DA.GetData(2, ref startDate_);
            DA.GetData(3, ref startTime_);
            DA.GetData(4, ref simDuration_);
            DA.GetData(5, ref windSpeed_);
            DA.GetData(6, ref windDirection_);
            DA.GetData(7, ref roughness_);
            DA.GetData(8, ref initialTemperature_);
            DA.GetData(9, ref specificHumidity_);
            DA.GetData(10, ref relativeHumidity_);

            // actions
            envimetSimulationFile.MainSettings baseSetting = new envimetSimulationFile.MainSettings()
            {
                SimName = simName_,
                INXfileAddress = _INXfileAddress,
                StartDate = startDate_,
                StartTime = startTime_,
                SimDuration = simDuration_,
                WindSpeed = windSpeed_,
                WindDir = windDirection_,
                Roughness = roughness_,
                InitialTemperature = initialTemperature_ + 273.15,
                SpecificHumidity = specificHumidity_,
                RelativeHumidity = relativeHumidity_
            };

            // OUTPUT
            DA.SetData(0, baseSetting);
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
                return DragonflyEnvimet.Properties.Resources.envimetConfigMainSettigs;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("d0519362-3b24-4f9f-b21b-e4af8741a72c"); }
        }
    }
}