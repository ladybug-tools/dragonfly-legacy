using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;
using System.IO;
using System.Text;
using System.Xml;

namespace DragonflyEnvimet
{
    public class XMLreader : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public XMLreader()
          : base("DF XML Reader", "DFXMLReader",
              "Use this component to see details about materials.\nConnect \"XML\" output of \"DF Library Reader\" and keywords to extract details. E.g. \"Density\", \"Description\"...",
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
            pManager.AddTextParameter("_XML", "_XML", "Output of \"DF Library Reader\".", GH_ParamAccess.item);
            pManager.AddTextParameter("_tagName", "_tagName", "A list of tag of the XML file you are reading.\nKeyword is a word of the XML file between <>", GH_ParamAccess.list);
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddTextParameter("InnerText", "InnerText", "InnerText of selected keyword.", GH_ParamAccess.list);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // INPUT
            // declaration
            string _XML = String.Empty;
            List<string> _tagName = new List<string>();

            DA.GetData(0, ref _XML);
            DA.GetDataList(1, _tagName);

            // actions
            XmlDocument xmlDoc = new XmlDocument();
            //declare tree
            Grasshopper.DataTree<string> intTree = new Grasshopper.DataTree<string>();

            xmlDoc.LoadXml(_XML);

            if (_tagName != null)
            {
                try
                {
                    //set up tree
                    for (int i = 0; i < _tagName.Count; i++)
                    {
                        Grasshopper.Kernel.Data.GH_Path pth = new Grasshopper.Kernel.Data.GH_Path(i);

                        var innerTextData = xmlDoc.GetElementsByTagName(_tagName[i])[0].InnerText;
                        intTree.Add(innerTextData, pth);
                    }

                    // output
                    DA.SetDataTree(0, intTree);

                }
                catch
                {
                    this.AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, "Please provide a valid keyword.");
                    return;
                }

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
                return DragonflyEnvimet.Properties.Resources.envimetXMLreader;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("664ac355-c4fb-406b-951f-4e8130ce1dab"); }
        }
    }
}