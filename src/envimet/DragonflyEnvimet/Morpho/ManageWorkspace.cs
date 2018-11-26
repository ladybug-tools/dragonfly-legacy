using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;
using envimentManagment;

namespace Morpho
{
    public class ManageWorkspace : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public ManageWorkspace()
          : base("DF Envimet Manage Workspace", "DFEnvimetManageWorkspace",
              "Use this component to create a Workspace folder",
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
            pManager.AddTextParameter("_workspaceFolder", "_workspaceFolder", "Main folder where you have to save an Envimet project.", GH_ParamAccess.item);
            pManager.AddTextParameter("_projectName_", "_projectName_", "Name of Envimet project folder where you have to save:\n1) EnviMet geometry file(*.INX)\n2) Configuration file(*.SIM)", GH_ParamAccess.item, "MorphoModel");
            pManager.AddTextParameter("ENVImetInstallFolder_", "ENVImetInstallFolder_", "Optional folder path for ENVImet4 installation folder.", GH_ParamAccess.item);
            pManager[2].Optional = true;
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddTextParameter("envimetFolder", "envimetFolder", "Envimet project folder. Connect it to \"_envimetFolder\" input of Dragonfly Envimet Spaces", GH_ParamAccess.item);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // INPUT
            // declaration
            string _workspaceFolder = null;
            string _projectName_ = "MorphoModel";
            string ENVImetInstallFolder_ = null;

            DA.GetData(0, ref _workspaceFolder);
            DA.GetData(1, ref _projectName_);
            DA.GetData(2, ref ENVImetInstallFolder_);

            // actions
            string mainDirectory = envimentManagment.WorkspaceFolderLB.findENVI_MET(ENVImetInstallFolder_);

            if (mainDirectory != null)
            {
                envimentManagment.WorkspaceFolderLB myFile = new envimentManagment.WorkspaceFolderLB(_workspaceFolder, _projectName_);
                string fullFolder = myFile.WorkspaceFolderLBwrite(mainDirectory);

                DA.SetData(0, fullFolder);
            }
            else
            {
                this.AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, "Envimet Main Folder not found!");
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
                return DragonflyEnvimet.Properties.Resources.envimetWorkspaceFolder;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("8259b879-e2e3-49d1-84e5-6635c5f717b6"); }
        }
    }
}