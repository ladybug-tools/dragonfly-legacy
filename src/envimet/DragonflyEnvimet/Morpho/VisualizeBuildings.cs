using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;
using System.Xml.Linq;
using System.Linq;

namespace DragonflyEnvimet
{
    public class VisualizeBuildings : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public VisualizeBuildings()
          : base("DF Visualize Buildings", "DFvisualizeBuildings",
              "Use this component to see buildings centroids of ENVI_MET model file.",
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
            pManager.AddTextParameter("_INXfileAddress", "_INXfileAddress", "Output of \"DF Envimet Spaces\".", GH_ParamAccess.item);
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddPointParameter("points", "points", "Points that represent buildings cells.", GH_ParamAccess.list);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // INPUT
            // declaration
            string _INXfileAddress = null;

            DA.GetData(0, ref _INXfileAddress);

            // action
            List<string> rowData = new List<string>();

            if (_INXfileAddress != null)
            {
                try
                {
                    XDocument doc = XDocument.Load(_INXfileAddress);
                    var descendants = doc.Descendants("buildingFlagAndNr");

                    foreach (var item in descendants)
                    {
                        string itemString = item.Value;

                        string[] listItem = itemString.Split('\n').Skip(1).ToArray();

                        rowData = listItem.ToList();
                        rowData.Remove("");
                    }

                    DA.SetDataList(0, generatePoints(rowData));
                }
                catch
                {
                    this.AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, "Something went wrong... only output from DF Envimet Spaces are supported now.");
                }
            }
        }

        public List<Point3d> generatePoints(List<string> righe)
        {
            List<Point3d> pts = new List<Point3d>();
            foreach (string row in righe)
            {
                string[] selString = row.Split(',');
                pts.Add(new Point3d(FromStringToDouble(selString[0]), FromStringToDouble(selString[1]), FromStringToDouble(selString[2])));
            }

            return pts;
        }

        public double FromStringToDouble(string inputString)
        {
            return Convert.ToDouble(inputString);
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
                return DragonflyEnvimet.Properties.Resources.envimetBuildingsVisualizerIcon;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("5aa2ef25-fb9b-4026-a4cd-c36f038e416f"); }
        }
    }
}