using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;
using envimetGrid;

namespace Morpho
{
    public class Grid : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public Grid()
          : base("DF Envimet Grid", "DFEnvimetGrid",
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
            pManager.AddGenericParameter("_telescope_", "_telescope_", "Choose telescope option if your Z domain can't be reached with equidistant Z grid. Default: 5 (growing percentage)", GH_ParamAccess.item);
            pManager.AddNumberParameter("startTelescopeHeight_", "startTelescopeHeight_", "Height where to start the telesscoping Z grid growth. Default: 5.0", GH_ParamAccess.item, 5.0);
            pManager.AddNumberParameter("dimX_", "dimX_", "Size of grid cell in meter. Default value is 3.0.", GH_ParamAccess.item, 3.0);
            pManager.AddNumberParameter("dimY_", "dimY_", "Size of grid cell in meter. Default value is 3.0.", GH_ParamAccess.item, 3.0);
            pManager.AddNumberParameter("dimZ_", "dimZ_", "Size of grid cell in meter. Default value is 3.0.", GH_ParamAccess.item, 3.0);
            pManager.AddIntegerParameter("addCellsLeft_", "addCellsLeft_", "Default: 2", GH_ParamAccess.item, 2);
            pManager.AddIntegerParameter("addCellslRight_", "addCellslRight_", "Default: 2", GH_ParamAccess.item, 2);
            pManager.AddIntegerParameter("addCellsUp_", "addCellsUp_", "Default: 2", GH_ParamAccess.item, 2);
            pManager.AddIntegerParameter("addCellsDown_", "addCellsDown_", "Default: 2", GH_ParamAccess.item, 2);
            pManager.AddIntegerParameter("numCellsZ_", "numCellsZ_", "// Number grid for Height domain. Default 15", GH_ParamAccess.item, 15);
            pManager.AddMeshParameter("baseSurface_", "baseSurface_", "If you do not want to generate grid using buildings connect a rectangular surface.", GH_ParamAccess.item);
            pManager[0].Optional = true;
            pManager[10].Optional = true;
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("envimentGrid", "envimentGrid", "Connect this output to \"Dragonfly Envimet Spaces\" in order to add grid input to ENVI-Met model.", GH_ParamAccess.item);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // INPUT
            // declaration
            double? _telescope_ = null;
            double startTelescopeHeight_ = 5.0;
            double dimX_ = 3.0;
            double dimY_ = 3.0;
            double dimZ_ = 3.0;
            int addCellsLeft_ = 2;
            int addCellslRight_ = 2;
            int addCellsDown_ = 2;
            int addCellsUp_ = 2;
            int numCellsZ_ = 15;
            Mesh baseSurface_ = null;

            DA.GetData(0, ref _telescope_);
            DA.GetData(1, ref startTelescopeHeight_);
            DA.GetData(2, ref dimX_);
            DA.GetData(3, ref dimY_);
            DA.GetData(4, ref dimZ_);
            DA.GetData(5, ref addCellsLeft_);
            DA.GetData(6, ref addCellslRight_);
            DA.GetData(7, ref addCellsDown_);
            DA.GetData(8, ref addCellsUp_);
            DA.GetData(9, ref numCellsZ_);
            DA.GetData(10, ref baseSurface_);


            // actions
            envimetGrid.AutoGrid myGrid = new envimetGrid.AutoGrid();

            if (_telescope_ != 0)
            {
                myGrid.telescope = _telescope_;
                if (_telescope_ >= 20.0)
                {
                    myGrid.ZGrids = myGrid.MaxZGrid - 1;
                    myGrid.telescope = 20.0;
                    this.AddRuntimeMessage(GH_RuntimeMessageLevel.Remark, "max telescope factor is 20.");
                }
            }

            if (dimX_ != 0)
                myGrid.DimX = dimX_;
            if (dimY_ != 0)
                myGrid.DimY = dimY_;
            if (dimZ_ != 0)
                myGrid.DimZ = dimZ_;

            if (startTelescopeHeight_ != 0)
                myGrid.StartTelescopeHeight = startTelescopeHeight_;
            if (addCellsLeft_ != 0)
                myGrid.ExtLeftXgrid = addCellsLeft_;
            if (addCellslRight_ > 0 || addCellslRight_ > 2)
                myGrid.ExtRightXgrid = addCellslRight_;
            if (addCellsUp_ > 0 || addCellsUp_ > 2)
                myGrid.ExtUpYgrid = addCellsUp_;
            if (addCellsDown_ > 0 || addCellsDown_ > 2)
                myGrid.ExtDownYgrid = addCellsDown_;
            if (numCellsZ_ > 0 || numCellsZ_ > 2)
                myGrid.ZGrids = numCellsZ_;
            if (numCellsZ_ >= myGrid.MaxZGrid)
                myGrid.ZGrids = myGrid.MaxZGrid - 1;

            myGrid.Surface = baseSurface_;

            // OUTPUT
            //DA.SetData(0, (object)envimetBuildings);
            DA.SetData(0, myGrid);

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
                return DragonflyEnvimet.Properties.Resources.envimetGridIcon;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("a1cb014a-b4ef-4886-988f-d6e1056c7a0a"); }
        }
    }
}