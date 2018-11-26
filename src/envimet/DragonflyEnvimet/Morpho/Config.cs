using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;
using System.Xml;
using System.Text;
using System.Linq;
using envimetSimulationFile;
using envimentManagment;

namespace DragonflyEnvimet
{
    public class Config : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public Config()
          : base("DF Envimet Config", "DFenvimetConfig",
              "This component writes simulation file (SIMX) of ENVI_MET.",
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
            pManager.AddGenericParameter("_mainSettings", "_mainSettings", "Location data which comes from \"Dragonfly Envimet Location\" component.", GH_ParamAccess.item);
            pManager.AddGenericParameter("simpleForcing_", "simpleForcing_", "Location data which comes from \"Dragonfly Envimet Location\" component.", GH_ParamAccess.item);

            pManager.AddBooleanParameter("parallel_", "parallel_", "Set True to increase the speed of calculation of ENVI_MET.\nThis option does not work with Basic version.\nDefault value is \"True\".", GH_ParamAccess.item, true);
            pManager.AddBooleanParameter("_runIt", "_runIt", "Set runIt to True to write SIMX file.\nDefault value is \"False\".", GH_ParamAccess.item, false);
            pManager[1].Optional = true;
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddTextParameter("SIMXfileAddress", "SIMXfileAddress", "The file path of the simx file that has been generated on your machine.", GH_ParamAccess.item);
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

            bool parallel_ = false;
            bool _runIt = false;

            envimetSimulationFile.MainSettings baseSetting = new envimetSimulationFile.MainSettings();
            envimetSimulationFile.SampleForcingSettings simpleForcing = new envimetSimulationFile.SampleForcingSettings(_dryBulbTemperature, _relativeHumidity);

            DA.GetData(0, ref baseSetting);
            DA.GetData(1, ref simpleForcing);
            DA.GetData(2, ref parallel_);
            DA.GetData(3, ref _runIt);

            // action
            // preparation
            var now = DateTime.Now;
            string revisionDate = now.ToString("yyyy.MM.dd HH:mm:ss");
            string destination = System.IO.Path.GetDirectoryName(baseSetting.INXfileAddress);
            string fileName = System.IO.Path.Combine(destination, baseSetting.SimName + ".simx");
            string[] empty = { };
            int simulationDuration = (simpleForcing.TotNumbers != 0) ? simpleForcing.TotNumbers : baseSetting.SimDuration;

            if (_runIt)
            {
                XmlTextWriter xWriter = new XmlTextWriter(fileName, Encoding.UTF8);

                // root
                xWriter.WriteStartElement("ENVI-MET_Datafile");
                xWriter.WriteString("\n ");

                // contents
                // Header section
                string headerTitle = "Header";
                string[] headerTag = new string[] { "filetype", "version", "revisiondate", "remark", "encryptionlevel" };
                string[] headerValue = new string[] { "SIMX", "1", revisionDate, "Created with lb_envimet", "0" };

                WriteINX.xmlSection(xWriter, headerTitle, headerTag, headerValue, 0, empty);


                // Main section
                string mainTitle = "mainData";
                string[] mainTag = new string[] { "simName", "INXFile", "filebaseName", "outDir", "startDate", "startTime", "simDuration", "windSpeed", "windDir", "z0", "T_H", "Q_H", "Q_2m" };
                string[] mainValue = new string[]
                  { baseSetting.SimName,
                    baseSetting.INXfileAddress,
                    baseSetting.SimName,
                    " ",
                    baseSetting.StartDate,
                    baseSetting.StartTime,
                    simulationDuration.ToString(),
                    baseSetting.WindSpeed.ToString(),
                    baseSetting.WindDir.ToString(),
                    baseSetting.Roughness.ToString(),
                    baseSetting.InitialTemperature.ToString(),
                    baseSetting.SpecificHumidity.ToString(),
                    baseSetting.RelativeHumidity.ToString()
                  };

                WriteINX.xmlSection(xWriter, mainTitle, mainTag, mainValue, 0, empty);


                // SimpleForcing section
                if (simpleForcing.TotNumbers != 0)
                {
                    string sfTitle = "SimpleForcing";
                    string[] sfTag = new string[] { "TAir", "Qrel" };
                    string[] sfValue = new string[] { simpleForcing.Temperature, simpleForcing.RelativeHumidity };

                    WriteINX.xmlSection(xWriter, sfTitle, sfTag, sfValue, 0, empty);
                }


                // Parallel section
                if (parallel_)
                {
                    string parallelTitle = "Parallel";
                    string[] parallelTag = new string[] { "CPUdemand" };
                    string[] parallelValue = new string[] { "ALL" };

                    WriteINX.xmlSection(xWriter, parallelTitle, parallelTag, parallelValue, 0, empty);
                }


                // close root and file
                xWriter.WriteEndElement();
                xWriter.Close();

                DA.SetData(0, fileName);
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
                return DragonflyEnvimet.Properties.Resources.envimetConfig;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("0c5fad2c-6139-4168-8e58-ea5711e95723"); }
        }
    }
}