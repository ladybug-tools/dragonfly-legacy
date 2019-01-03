using Rhino;
using System;
using System.Xml;
using System.Linq;
using System.Text;
using Rhino.Geometry;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Text.RegularExpressions;

/**********************************************************
  ENVI_MET Grid
***********************************************************/
namespace envimetGrid
{
    public class AutoGrid
    {
        public double? telescope;

        public int ZGrids { get; set; }
        public double DimX { get; set; }
        public double DimY { get; set; }
        public double DimZ { get; set; }
        public double StartTelescopeHeight { get; set; }
        public int ExtLeftXgrid { get; set; }
        public int ExtRightXgrid { get; set; }
        public int ExtUpYgrid { get; set; }
        public int ExtDownYgrid { get; set; }

        public Mesh Surface { get; set; }

        public static int NumX;
        public static int NumY;
        public static double[] ZNumbers;

        public double MinX { get; private set; }
        public double MaxX { get; private set; }
        public double MinY { get; private set; }
        public double MaxY { get; private set; }
        public int MaxZGrid { get; }

        public AutoGrid()
        {
            this.ZGrids = 15;
            this.DimX = 3.0;
            this.DimY = 3.0;
            this.DimZ = 3.0;
            this.StartTelescopeHeight = 5.0;
            this.ExtLeftXgrid = 2;
            this.ExtRightXgrid = 2;
            this.ExtUpYgrid = 2;
            this.ExtDownYgrid = 2;
            this.MaxZGrid = 999;
            this.MinX = 0;
            this.MaxX = 0;
            this.MinY = 0;
            this.MaxY = 0;
            this.telescope = null;

            if (!this.telescope.HasValue)
                this.ZGrids += 4;

            if (this.ExtLeftXgrid < 2)
                this.ExtLeftXgrid = 2;
            if (this.ExtRightXgrid < 2)
                this.ExtRightXgrid = 2;
            if (this.ExtUpYgrid < 2)
                this.ExtUpYgrid = 2;
            if (this.ExtDownYgrid < 2)
                this.ExtDownYgrid = 2;
            if (this.ExtDownYgrid < 2)
                this.ExtDownYgrid = 2;
        }

        public void gZmethod(List<Mesh> buildings)
        {
            double distLeft = this.ExtLeftXgrid * this.DimX;
            double distRight = this.ExtRightXgrid * this.DimX;
            double distUp = this.ExtUpYgrid * this.DimY;
            double distDown = this.ExtDownYgrid * this.DimY;

            this.MinX = this.MinY = 10000000;
            this.MaxX = this.MaxY = -10000000;
            double maxZ = -10000000;

            foreach (Mesh geo in buildings)
            {
                BoundingBox BB1 = geo.GetBoundingBox(true);
                if (this.MinX > BB1.Min.X)
                    this.MinX = BB1.Min.X;
                if (this.MaxX < BB1.Max.X)
                    this.MaxX = BB1.Max.X;
                if (this.MinY > BB1.Min.Y)
                    this.MinY = BB1.Min.Y;
                if (this.MaxY < BB1.Max.Y)
                    this.MaxY = BB1.Max.Y;
                if (maxZ < BB1.Max.Z)
                    maxZ = BB1.Max.Z;
            }

            // Geometry BoundingBox limits NETO
            this.MinX = this.MinX - distLeft;
            this.MinY = this.MinY - distDown;
            this.MaxX = this.MaxX + distRight;
            this.MaxY = this.MaxY + distUp;

            // Required height -- Twice the heighest building
            double reqHeight = maxZ * 2;
            double domX = this.MaxX - this.MinX;
            double domY = this.MaxY - this.MinY;
            NumX = (int)(domX / this.DimX);
            NumY = (int)(domY / this.DimY);

            // Reccalculate maxX/Y just for the bounding box fit the grid size/length
            this.MaxX = this.MinX + (NumX * this.DimX);
            this.MaxY = this.MinY + (NumY * this.DimY);

            // Calculate z info
            // Preparation
            double[] gZ = new double[this.ZGrids];
            double dimZ = this.DimZ;
            double firstGrid = dimZ / 5;
            double grid = 0;
            // Calculate
            for (int i = 1; i < this.ZGrids + 1; i++)
            {
                if (this.telescope == null)
                {
                    switch (i)
                    {
                        case 1:
                            gZ[i - 1] = firstGrid / 2;
                            break;
                        case 2:
                        case 3:
                        case 4:
                        case 5:
                            gZ[i - 1] = (i * firstGrid) - (firstGrid / 2);
                            break;
                        default:
                            gZ[i - 1] = ((i - 4) * dimZ) - (dimZ / 2);
                            break;
                    }
                }
                else
                {
                    if (i == 1 || grid <= this.StartTelescopeHeight)
                    {
                        grid = (i * dimZ) - (dimZ / 2);
                    }
                    else
                    {
                        double g1 = grid;
                        double gz = dimZ;
                        dimZ = dimZ + (dimZ * (double)this.telescope / 100);
                        grid = grid + (dimZ + gz) / 2;
                    }
                    gZ[i - 1] = grid;
                }
            }
            ZNumbers = gZ;
        }

        public List<Point3d> GridXY()
        {
            List<Point3d> gridPoints = new List<Point3d>();
            // XY Grid
            for (int ix = 0; ix < NumX + 1; ix++)
                for (int iy = 0; iy < NumY + 1; iy++)
                    gridPoints.Add(new Point3d((ix * this.DimX) + this.MinX, (iy * this.DimY) + this.MinY, ZNumbers[0]));
            return gridPoints;
        }

        public List<Point3d> GridXZ()
        {
            List<Point3d> gridPoints = new List<Point3d>();
            // XZ Grid
            for (int ix = 0; ix < NumX + 1; ix++)
                for (int iz = 0; iz < this.ZGrids; iz++)
                    gridPoints.Add(new Point3d((ix * this.DimX) + this.MinX, this.MaxY, ZNumbers[iz]));

            return gridPoints;
        }

        public List<Point3d> GridYZ()
        {
            List<Point3d> gridPoints = new List<Point3d>();
            // YZ Grid
            for (int iy = 0; iy < NumY + 1; iy++)
                for (int iz = 0; iz < this.ZGrids; iz++)
                    gridPoints.Add(new Point3d(this.MaxX, (iy * this.DimY) + this.MinY, ZNumbers[iz]));

            return gridPoints;
        }

        public int[,,] BasePoints(Mesh M, int index, double T, ref string buildingFlagAndNr)
        {
            List<Plane> planes = new List<Plane>();
            string[] checkZ = new string[ZNumbers.Length]; // for casting precision

            for (int i = 0; i < ZNumbers.Length; i++)
            {
                Plane pl = new Plane(new Point3d(0, 0, ZNumbers[i]), Vector3d.ZAxis);
                planes.Add(pl);
                checkZ[i] = ZNumbers[i].ToString("0.00");
            }

            // internal method
            List<Point3d> gridXY = this.GridXY();

            Polyline[] polilinee = Rhino.Geometry.Intersect.Intersection.MeshPlane(M, planes);

            List<Curve> polilineeList = new List<Curve>();
            foreach (Polyline cr in polilinee)
                polilineeList.Add(cr.ToPolylineCurve());

            Brep[] superfici = Rhino.Geometry.Brep.CreatePlanarBreps(polilineeList, T);

            // BBox
            BoundingBox bbox = M.GetBoundingBox(false);

            List<Point3d> pointForProjection = new List<Point3d>();

            // small scaled grid
            foreach (Point3d pt in gridXY)
                if (pt.X >= bbox.Min.X - this.DimX && pt.X <= bbox.Max.X + this.DimX)
                    if (pt.Y >= bbox.Min.Y - this.DimY && pt.Y <= bbox.Max.Y + this.DimY)
                        pointForProjection.Add(new Point3d(pt.X, pt.Y, 0));

            // from array to list
            List<Brep> volume = new List<Brep>(superfici);

            Point3d[] voxelPoints = Rhino.Geometry.Intersect.Intersection.ProjectPointsToBreps(volume, pointForProjection, Vector3d.ZAxis, T);

            // bulk rect array
            int[,,] grid3d = new int[NumX + 1, NumY + 1, ZNumbers.Length];

            foreach (Point3d pt in voxelPoints)
            {
                int valX = (int)Math.Round(((pt.X - this.MinX) / this.DimX), 0);
                int valY = (int)Math.Round(((pt.Y - this.MinY) / this.DimY), 0);
                int valZ = Array.IndexOf(checkZ, pt.Z.ToString("0.00"));
                grid3d[valX, valY, valZ] = index;
                buildingFlagAndNr += String.Format("{0},{1},{2},{3},{4}\n", valX, valY, valZ, 1, index);
            }

            voxelPoints = null;
            pointForProjection = null;

            return grid3d;
        }

        public int[,] BasePoints2d(Brep Geo, int index, double T)
        {

            int[,] grid2d = new int[NumX + 1, NumY + 1];

            for (int i = 0; i < NumX + 1; i++)
                for (int j = 0; j < NumY + 1; j++)
                {
                    Point3d point = new Point3d((i * this.DimX) + this.MinX, (j * this.DimY) + this.MinY, 0);
                    Line ln = new Line(point, Rhino.Geometry.Vector3d.ZAxis, this.DimX * 2);

                    // projection
                    Transform projection = Rhino.Geometry.Transform.PlanarProjection(Rhino.Geometry.Plane.WorldXY);
                    Geo.Transform(projection);

                    Point3d[] intersection_points;
                    Curve[] overlap_curves;

                    if (Rhino.Geometry.Intersect.Intersection.CurveBrep(ln.ToNurbsCurve(), Geo, T, out overlap_curves, out intersection_points))
                        if (overlap_curves.Length > 0 || intersection_points.Length > 0)
                        {
                            grid2d[i, j] = index;
                        }
                        else
                        {
                            grid2d[i, j] = 0;
                        }
                }
            return grid2d;
        }

        public int[,] mergeMatrix2d(List<int[,]> arrayList)
        {
            int[,] integerMatrix = new int[NumX + 1, NumY + 1];

            for (int ii = 0; ii < arrayList.Count; ii++)
            {
                int[,] list = arrayList[ii];
                for (int i = 0; i < NumX + 1; i++)
                {
                    for (int j = 0; j < NumY + 1; j++)
                    {
                        // Add cell togheter and overlap workaround
                        integerMatrix[i, j] += list[i, j];
                        if (integerMatrix[i, j] >= arrayList.Count + 1)
                        {
                            integerMatrix[i, j] = integerMatrix[i, j] - 1;
                        }
                    }
                }
            }

            return integerMatrix;
        }

        public int[,,] mergeMatrix(List<int[,,]> arrayList)
        {
            int[,,] integerMatrix = new int[NumX + 1, NumY + 1, ZNumbers.Length];

            for (int ii = 0; ii < arrayList.Count; ii++)
            {
                int[,,] list = arrayList[ii];
                for (int i = 0; i < NumX + 1; i++)
                    for (int j = 0; j < NumY + 1; j++)
                        for (int k = 0; k < ZNumbers.Length; k++)
                        {
                            // Add cell togheter and overlap workaround
                            integerMatrix[i, j, k] += list[i, j, k];
                            if (integerMatrix[i, j, k] >= arrayList.Count + 1)
                                integerMatrix[i, j, k] = 0;
                        }
            };

            return integerMatrix;
        }

        public static string View2dMatrix(int[,] Data)
        {
            // flip and traspose
            string visualMatrix = string.Empty;

            for (int j = NumY; j >= 0; j--)
            {
                string[] line = new string[NumX + 1];
                for (int i = 0; i < NumX + 1; i++)
                {
                    line[i] = Data[i, j].ToString();
                }
                string row = String.Join(",", line);
                row += "\n";
                visualMatrix += row;
            }
            return visualMatrix;
        }

        public static string EmptyMatrix(string element)
        {
            // flip and traspose
            string visualMatrix = string.Empty;

            for (int j = NumY; j >= 0; j--)
            {
                string[] line = new string[NumX + 1];
                for (int i = 0; i < NumX + 1; i++)
                {
                    line[i] = "";
                }
                string row = String.Join(",", line);
                row += "\n";
                visualMatrix += row;
            }
            return visualMatrix;
        }
    }

    /**********************************************************
      ENVI_MET Buildings
    ***********************************************************/

    public class BuildingMatrix : AutoGrid
    {

        private List<string> wallMaterial = new List<string>();
        private List<string> roofMaterial = new List<string>();
        public readonly List<string> greenWallMaterial = new List<string>();
        public readonly List<string> greenRoofMaterial = new List<string>();

        public string CommonWallMaterial { get; set; }
        public string CommonRoofMaterial { get; set; }
        // GREEN material
        private const string greenNullMaterial = " ";
        public readonly List<string> selectedWallMaterialGreenings = new List<string>();
        public readonly List<string> selectedRoofMaterialGreenings = new List<string>();

        public List<Mesh> Buildings { get; set; }
        public List<int> GreenIdBuildings { get; set; }

        public delegate int[,] BuildingMatrix2d(int[,,] Data);

        public BuildingMatrix(List<Mesh> buildings, List<string> wall, List<string> roof, string commonWallMaterial, string commonRoofMaterial, List<int> greenBuildingsId, List<string> greenWall, List<string> greenRoof)
        {
            this.Buildings = buildings;
            this.GreenIdBuildings = greenBuildingsId;

            this.CommonWallMaterial = commonWallMaterial;
            this.CommonRoofMaterial = commonRoofMaterial;

            // Building normal materials
            if (buildings.Count == wall.Count && buildings.Count == roof.Count)
            {
                for (int i = 0; i < buildings.Count; i++)
                {
                    this.wallMaterial.Add(wall[i]);
                    this.roofMaterial.Add(roof[i]);
                }
            }
            else if (roof.Count == 1 && buildings.Count == wall.Count)
            {
                for (int i = 0; i < buildings.Count; i++)
                {
                    this.wallMaterial.Add(wall[i]);
                    this.roofMaterial.Add(this.CommonRoofMaterial);
                }
            }
            else if (wall.Count == 1 && buildings.Count == roof.Count)
            {
                for (int i = 0; i < buildings.Count; i++)
                {
                    this.wallMaterial.Add(this.CommonWallMaterial);
                    this.roofMaterial.Add(roof[i]);
                }
            }
            else
            {
                for (int i = 0; i < buildings.Count; i++)
                {
                    this.wallMaterial.Add(this.CommonWallMaterial);
                    this.roofMaterial.Add(this.CommonRoofMaterial);
                }
            }

            // Green materials
            if (greenBuildingsId.Count != 0)
            {
                // normal material for buildings
                foreach (int index in greenBuildingsId)
                {
                    this.selectedWallMaterialGreenings.Add(this.wallMaterial[index]);
                    this.selectedRoofMaterialGreenings.Add(this.roofMaterial[index]);
                }

                if (greenBuildingsId.Count == greenWall.Count && greenBuildingsId.Count == greenRoof.Count)
                    for (int i = 0; i < greenBuildingsId.Count; i++)
                    {
                        this.greenWallMaterial.Add(greenWall[i]);
                        this.greenRoofMaterial.Add(greenRoof[i]);
                    }
                else if (greenRoof.Count == 0 && greenBuildingsId.Count == greenWall.Count)
                {
                    for (int i = 0; i < greenBuildingsId.Count; i++)
                    {
                        this.greenWallMaterial.Add(greenWall[i]);
                        this.greenRoofMaterial.Add(greenNullMaterial);
                    }
                }
                else if (greenWall.Count == 0 && greenBuildingsId.Count == greenRoof.Count)
                {
                    for (int i = 0; i < greenBuildingsId.Count; i++)
                    {
                        this.greenWallMaterial.Add(greenNullMaterial);
                        this.greenRoofMaterial.Add(greenRoof[i]);
                    }
                }
                else if (greenWall.Count == 0 && greenRoof.Count == 1)
                {
                    for (int i = 0; i < greenBuildingsId.Count; i++)
                    {
                        this.greenWallMaterial.Add(greenNullMaterial);
                        this.greenRoofMaterial.Add(greenRoof[0]);
                    }
                }
                else if (greenRoof.Count == 0 && greenWall.Count == 1)
                {
                    for (int i = 0; i < greenBuildingsId.Count; i++)
                    {
                        this.greenWallMaterial.Add(greenWall[0]);
                        this.greenRoofMaterial.Add(greenNullMaterial);
                    }
                }
                else if (greenWall.Count == 1 && greenRoof.Count == 1)
                {
                    for (int i = 0; i < greenBuildingsId.Count; i++)
                    {
                        this.greenWallMaterial.Add(greenWall[0]);
                        this.greenRoofMaterial.Add(greenRoof[0]);
                    }
                }
                else
                {
                    for (int i = 0; i < greenBuildingsId.Count; i++)
                    {
                        this.greenWallMaterial.Add(greenNullMaterial);
                        this.greenRoofMaterial.Add(greenNullMaterial);
                    }
                }
            }
        }

        private string SparseMatrix(int[,,] pts, List<string> w, List<string> r)
        {
            string matrice = string.Empty;
            for (int i = 0; i < NumX + 1; i++)
                for (int j = 0; j < NumY + 1; j++)
                    for (int k = 0; k < ZNumbers.Length; k++)
                    {
                        string line = string.Empty;
                        int index = 0;
                        int indexW = 0;
                        int indexR = 0;
                        if (pts[i, j, k] != 0)
                        {
                            index = pts[i, j, k] - 1;
                            try
                            {
                                if (pts[i - 1, j, k] == 0 && pts[i, j - 1, k] == 0 && pts[i, j, k - 1] == 0)
                                {
                                    line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, w[index], w[index], r[index]);
                                }
                                else if (pts[i - 1, j, k] == 0 && pts[i, j - 1, k] != 0 && pts[i, j, k - 1] == 0)
                                {
                                    line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, w[index], "", r[index]);
                                }
                                else if (pts[i - 1, j, k] != 0 && pts[i, j - 1, k] == 0 && pts[i, j, k - 1] == 0)
                                {
                                    line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, "", w[index], r[index]);
                                }
                                else if (pts[i - 1, j, k] == 0 && pts[i, j - 1, k] == 0 && pts[i, j, k - 1] != 0)
                                {
                                    line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, w[index], w[index], "");
                                }
                                else if (pts[i - 1, j, k] == 0 && pts[i, j - 1, k] != 0 && pts[i, j, k - 1] != 0)
                                {
                                    line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, w[index], "", "");
                                }
                                else if (pts[i - 1, j, k] != 0 && pts[i, j - 1, k] != 0 && pts[i, j, k - 1] == 0)
                                {
                                    line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, "", "", r[index]);
                                }
                                else if (pts[i - 1, j, k] != 0 && pts[i, j - 1, k] == 0 && pts[i, j, k - 1] != 0)
                                {
                                    line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, "", w[index], "");
                                }
                            }
                            catch (IndexOutOfRangeException)
                            {
                                if (pts[i - 1, j, k] == 0 && pts[i, j - 1, k] == 0 && k == 0)
                                {
                                    line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, w[index], w[index], r[index]);
                                }
                                else if (pts[i - 1, j, k] == 0 && pts[i, j - 1, k] != 0 && k == 0)
                                {
                                    line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, w[index], "", r[index]);
                                }
                                else if (pts[i - 1, j, k] != 0 && pts[i, j - 1, k] == 0 && k == 0)
                                {
                                    line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, "", w[index], r[index]);
                                }
                                else if (pts[i - 1, j, k] != 0 && pts[i, j - 1, k] != 0 && k == 0)
                                {
                                    line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, "", "", r[index]);
                                }
                            }
                        }
                        else
                        {
                            if (i != 0 && j != 0)
                                try
                                {
                                    if (pts[i - 1, j, k] != 0 && pts[i, j - 1, k] == 0 && pts[i, j, k - 1] == 0)
                                    {
                                        index = pts[i - 1, j, k] - 1;
                                        line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, w[index], "", "");
                                    }
                                    else if (pts[i - 1, j, k] == 0 && pts[i, j - 1, k] != 0 && pts[i, j, k - 1] == 0)
                                    {
                                        index = pts[i, j - 1, k] - 1;
                                        line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, "", w[index], "");
                                    }
                                    else if (pts[i - 1, j, k] == 0 && pts[i, j - 1, k] == 0 && pts[i, j, k - 1] != 0)
                                    {
                                        index = pts[i, j, k - 1] - 1;
                                        line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, "", "", r[index]);
                                    }
                                    else if (pts[i - 1, j, k] != 0 && pts[i, j - 1, k] != 0 && pts[i, j, k - 1] == 0)
                                    {
                                        index = pts[i, j - 1, k] - 1;
                                        line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, w[index], w[index], "");
                                    }
                                    else if (pts[i - 1, j, k] != 0 && pts[i, j - 1, k] == 0 && pts[i, j, k - 1] != 0)
                                    {
                                        indexW = pts[i - 1, j, k] - 1;
                                        indexR = pts[i, j, k - 1] - 1;
                                        line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, w[indexW], "", r[indexR]);
                                    }
                                    else if (pts[i - 1, j, k] == 0 && pts[i, j - 1, k] != 0 && pts[i, j, k - 1] != 0)
                                    {
                                        indexW = pts[i, j - 1, k] - 1;
                                        indexR = pts[i, j, k - 1] - 1;
                                        line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, "", w[indexW], r[indexR]);
                                    }
                                    else if (pts[i - 1, j, k] != 0 && pts[i, j - 1, k] != 0 && pts[i, j, k - 1] != 0)
                                    {
                                        indexW = pts[i, j - 1, k] - 1;
                                        indexR = pts[i, j, k - 1] - 1;
                                        line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, w[indexW], w[indexW], r[indexR]);
                                    }
                                }
                                catch (IndexOutOfRangeException)
                                {
                                    if (pts[i - 1, j, k] != 0 && pts[i, j - 1, k] == 0 && k == 0)
                                    {
                                        index = pts[i - 1, j, k] - 1;
                                        line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, w[index], "", "");
                                    }
                                    else if (pts[i - 1, j, k] == 0 && pts[i, j - 1, k] != 0 && k == 0)
                                    {
                                        index = pts[i, j - 1, k] - 1;
                                        line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, "", w[index], "");
                                    }
                                    else if (pts[i - 1, j, k] != 0 && pts[i, j - 1, k] != 0 && k == 0)
                                    {
                                        index = pts[i, j - 1, k] - 1;
                                        line = String.Format("{0},{1},{2},{3},{4},{5}\n", i, j, k, w[index], w[index], "");
                                    }
                                }
                        }
                        matrice += line;
                    }
            return matrice;
        }

        public string NormalSparseMatrix(int[,,] pts)
        {
            string matrice = this.SparseMatrix(pts, this.wallMaterial, this.roofMaterial);
            return matrice;
        }

        public string GreenSparseMatrix(int[,,] pts)
        {
            string matrice = this.SparseMatrix(pts, this.greenWallMaterial, this.greenRoofMaterial);
            return matrice;
        }

        // Bulding matrix implementation
        public int[,] BuildingId2d(int[,,] Data)
        {

            int[,] grid2d = new int[NumX + 1, NumY + 1];

            for (int i = 0; i < NumX + 1; i++)
            {
                int[] id = new int[ZNumbers.Length];
                for (int j = 0; j < NumY + 1; j++)
                {
                    for (int k = 0; k < ZNumbers.Length; k++)
                    {
                        id[k] = Data[i, j, k];
                    }
                    grid2d[i, j] = id.Max();
                }
            }

            return grid2d;
        }

        public int[,] BuildingBottom2d(int[,,] Data)
        {

            int[,] grid2d = new int[NumX + 1, NumY + 1];

            for (int i = 0; i < NumX + 1; i++)
            {
                int[] bottom = new int[ZNumbers.Length];
                for (int j = 0; j < NumY + 1; j++)
                {
                    for (int k = 0; k < ZNumbers.Length; k++)
                    {
                        bottom[k] = (Data[i, j, k] != 0) ? k : 99999999;
                    }
                    int min = bottom.Min();
                    grid2d[i, j] = (min != 99999999) ? (int)Math.Round(ZNumbers[min], 0) : 0;
                }
            }

            return grid2d;
        }

        public int[,] BuildingTop2d(int[,,] Data)
        {

            int[,] grid2d = new int[NumX + 1, NumY + 1];


            for (int i = 0; i < NumX + 1; i++)
            {
                int[] up = new int[ZNumbers.Length];
                for (int j = 0; j < NumY + 1; j++)
                {
                    for (int k = 0; k < ZNumbers.Length; k++)
                    {
                        up[k] = (Data[i, j, k] != 0) ? (int)Math.Round(ZNumbers[k], 0) : 0;
                    }
                    int max = up.Max();
                    grid2d[i, j] = max;
                }
            }

            return grid2d;
        }
    }


    /**********************************************************
      ENVI_MET 2d elements
    ***********************************************************/

    public class Element2dMatrix : AutoGrid
    {

        // variabili di istanza
        protected List<string> customMaterial = new List<string>();
        public List<Brep> Geometries { get; set; }
        public string DefaultMaterial { get; set; }

        public Element2dMatrix(string defaultMaterial, List<string> customMaterialList, List<Brep> geometries)
        {
            this.DefaultMaterial = defaultMaterial;
            this.Geometries = geometries;

            if (geometries.Count == customMaterialList.Count)
            {
                for (int i = 0; i < geometries.Count; i++)
                {
                    this.customMaterial.Add(customMaterialList[i]); // custom materials
                }
            }
            else if (geometries.Count != customMaterialList.Count && customMaterialList.Count == 1)
            {
                for (int i = 0; i < geometries.Count; i++)
                {
                    this.customMaterial.Add(customMaterialList[0]); // only one custom material ALL
                }
            }
            else
            {
                for (int i = 0; i < geometries.Count; i++)
                {
                    this.customMaterial.Add(this.DefaultMaterial); // default material ALL
                }
            }
        }


        public string MatrixWithMaterials(int[,] Data)
        {
            // flip and traspose
            string visualMatrix = string.Empty;

            for (int j = NumY; j >= 0; j--)
            {
                string[] line = new string[NumX + 1];
                for (int i = 0; i < NumX + 1; i++)
                {
                    string valore = string.Empty;
                    if (Data[i, j] != 0)
                    {
                        valore = this.customMaterial[Data[i, j] - 1];
                    }
                    else
                    {
                        valore = this.DefaultMaterial;
                    }
                    line[i] = valore;
                }
                string row = String.Join(",", line);
                row += "\n";
                visualMatrix += row;
            }
            return visualMatrix;
        }
    }

    public class ThreeDimensionalPlants : Element2dMatrix
    {
        private List<string[]> propertiesTree = new List<string[]>();

        public List<string[]> PropertiesTree
        {
            get { return propertiesTree; }
        }
        public List<Brep> Threes { get; set; }

        public ThreeDimensionalPlants(string defaultMaterial, List<string> customMaterialList, List<Brep> geometries) : base(defaultMaterial, customMaterialList, geometries)
        {
            this.Threes = geometries;
        }

        public void GenerateLists(int[,] Data)
        {
            for (int i = 0; i < NumX + 1; i++)
            {
                for (int j = NumY; j > 0; j--)
                {
                    if (Data[i, j] != 0)
                    {
                        string[] idAndDescription = this.customMaterial[Data[i, j] - 1].Split(',');
                        this.propertiesTree.Add(new string[] { (i + 1).ToString(), (j + 1).ToString(), "0", idAndDescription[0], idAndDescription[1], "0" });
                    }
                }
            }
        }
    }

    public class NestingGrid
    {

        public int NumNestingGrid { get; set; }
        public string SoilProfileA { get; set; }
        public string SoilProfileB { get; set; }
        public string Name { get; set; }

        public NestingGrid()
        {
            this.NumNestingGrid = 3;
            this.SoilProfileA = "0000LO";
            this.SoilProfileB = "0000LO";
            this.Name = "NestingGrid";
        }
    }
}

/**********************************************************
  ENVI_MET Managment
***********************************************************/
namespace envimentManagment
{
    public class WorkspaceFolderLB
    {
        private string workspaceFolder;
        private string projectFolderName;
        private string fileNamePrj;
        private string iniFileName;
        private string worspaceName;
        private string projectName;
        private string edbFileName;


        public WorkspaceFolderLB(string workspaceFolder, string projectFolderName)
        {
            this.workspaceFolder = workspaceFolder;
            this.projectFolderName = projectFolderName;
            this.fileNamePrj = System.Environment.MachineName + ".projects";
            this.iniFileName = "envimet.ini";
            this.worspaceName = "workspace.infoX";
            this.projectName = "project.infoX";
            this.edbFileName = "projectdatabase.edb";
        }

        public string WorkspaceFolderLBwrite(string mainDirectory)
        {
            // date
            var now = DateTime.Now;

            // complete path
            string fullFolder = System.IO.Path.Combine(this.workspaceFolder, this.projectFolderName);

            // check folder
            if (!(System.IO.Directory.Exists(fullFolder)))
            {
                System.IO.Directory.CreateDirectory(fullFolder);
            }

            // create project
            string prjFile = System.IO.Path.Combine(mainDirectory, this.fileNamePrj);
            System.IO.File.WriteAllText(prjFile, fullFolder);


            // INI and workspace file
            string iniFile = System.IO.Path.Combine(mainDirectory, this.iniFileName);
            string workspaceXml = System.IO.Path.Combine(mainDirectory, this.worspaceName);
            string projectFileInFolder = System.IO.Path.Combine(fullFolder, this.projectName);
            string edbFileInFolder = System.IO.Path.Combine(fullFolder, this.edbFileName);

            // iniFile
            string[] textIniFile = { "[projectdir]", String.Format("dir={0}", this.workspaceFolder) };
            System.IO.File.WriteAllLines(iniFile, textIniFile);

            // workspaceXml
            string[] textWorkspaceXml = {"<ENVI-MET_Datafile>", "<Header>", "<filetype>workspacepointer</filetype>",
        "<version>6811715</version>", String.Format("<revisiondate>{0}</revisiondate>", now.ToString("yyyy-MM-dd HH:mm:ss")),
        "<remark></remark>", "<encryptionlevel>5150044</encryptionlevel>", "</Header>",
        "<current_workspace>", String.Format("<absolute_path> {0} </absolute_path>", this.workspaceFolder),
        String.Format("<last_active> {0} </last_active>", this.projectFolderName), "</current_workspace>", "</ENVI-MET_Datafile>"};
            System.IO.File.WriteAllLines(workspaceXml, textWorkspaceXml);

            // projectFileInFolder
            string[] textProjectFileInFolder = {"<ENVI-MET_Datafile>", "<Header>", "<filetype>infoX ENVI-met Project Description File</filetype>",
        "<version>4240697</version>", String.Format("<revisiondate>{0}</revisiondate>", now.ToString("yyyy-MM-dd HH:mm:ss")),
        "<remark></remark>", "<encryptionlevel>5220697</encryptionlevel>", "</Header>",
        "<project_description>", String.Format("<name> {0} </name>", this.projectFolderName),
        "<description>  </description>", "<useProjectDB> 1 </useProjectDB>", "</project_description>", "</ENVI-MET_Datafile>"};
            System.IO.File.WriteAllLines(projectFileInFolder, textProjectFileInFolder);

            // edbFileInFolder
            string[] textEdbFileInFolder = {"<ENVI-MET_Datafile>", "<Header>", "<filetype>DATA</filetype>",
        "<version>1</version>", String.Format("<revisiondate>{0}</revisiondate>", now.ToString("yyyy-MM-dd HH:mm:ss")),
        "<remark>Envi-Data</remark>", "<encryptionlevel>1701377</encryptionlevel>",
        "</Header>", "</ENVI-MET_Datafile>"};
            System.IO.File.WriteAllLines(edbFileInFolder, textEdbFileInFolder);

            return fullFolder;
        }

        public static string findENVI_MET(string ENVImetInstallFolder)
        {

            string root = System.IO.Path.GetPathRoot(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData));
            string directory = System.IO.Path.Combine(root, "ENVImet4\\sys.basedata\\");

            // custom forlder
            if (ENVImetInstallFolder != null)
            {
                directory = System.IO.Path.Combine(ENVImetInstallFolder, "sys.basedata\\");
            }

            if (System.IO.Directory.Exists(directory))
            {
                return directory;
            }
            else
            {
                return null;
            }
        }


        public static string getSetDestinationFolder()
        {
            string appDataFolder = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
            string destinationFolder = System.IO.Path.Combine(appDataFolder, "DragonflyEnvimet");

            // create folder if not exist
            if (!(System.IO.Directory.Exists(destinationFolder)))
                System.IO.Directory.CreateDirectory(destinationFolder);

            return destinationFolder;
        }

    }


    public class WriteINX
    {

        static public void xmlSection(XmlTextWriter w, string sectionTitle, string[] tags, string[] values, int flag, string[] attributes)
        {

            w.WriteStartElement(sectionTitle);
            w.WriteString("\n ");
            foreach (var item in tags.Zip(values, (a, b) => new { A = a, B = b }))
            {
                if (flag == 0)
                {
                    w.WriteStartElement(item.A);
                    w.WriteString(item.B);
                    w.WriteEndElement();
                }
                else if (flag == 1)
                {
                    w.WriteStartElement(item.A);
                    w.WriteAttributeString("", "type", null, attributes[0]);
                    w.WriteAttributeString("", "dataI", null, attributes[1]);
                    w.WriteAttributeString("", "dataJ", null, attributes[2]);
                    w.WriteString(item.B);
                    w.WriteEndElement();
                }
                else
                {
                    w.WriteStartElement(item.A);
                    w.WriteAttributeString("", "type", null, attributes[0]);
                    w.WriteAttributeString("", "dataI", null, attributes[1]);
                    w.WriteAttributeString("", "dataJ", null, attributes[2]);
                    w.WriteAttributeString("", "zlayers", null, attributes[3]);
                    w.WriteAttributeString("", "defaultValue", null, attributes[4]);
                    w.WriteString(item.B);
                    w.WriteEndElement();
                }
                w.WriteString("\n ");

            }
            w.WriteEndElement();
            w.WriteString("\n");
        }


        static public string Element2dCalculation(envimetGrid.Element2dMatrix envimentObj, envimetGrid.AutoGrid myGrid, double tol)
        {

            List<int[,]> elementList = new List<int[,]>();

            foreach (Brep el in envimentObj.Geometries)
            {
                int index = envimentObj.Geometries.IndexOf(el) + 1;
                int[,] grid2d = myGrid.BasePoints2d(el, index, tol);
                elementList.Add(grid2d);
            }

            int[,] integerMatrix = myGrid.mergeMatrix2d(elementList);

            string matriceEnvimet = envimentObj.MatrixWithMaterials(integerMatrix);

            return matriceEnvimet;

        }

        static public void Three3dCalculation(envimetGrid.ThreeDimensionalPlants envimentObj, envimetGrid.AutoGrid myGrid, double tol)
        {

            List<int[,]> elementList = new List<int[,]>();

            foreach (Brep el in envimentObj.Threes)
            {
                int index = envimentObj.Threes.IndexOf(el) + 1;
                int[,] grid2d = myGrid.BasePoints2d(el, index, tol);
                elementList.Add(grid2d);
            }

            int[,] integerMatrix = myGrid.mergeMatrix2d(elementList);
            envimentObj.GenerateLists(integerMatrix);

        }

        public static string BuildingCalculation(envimetGrid.BuildingMatrix edifici, envimetGrid.AutoGrid myGrid, double tol, ref string dbMatrix, ref string vBuildingMatrixId, ref string vBuildingMatrixBottom, ref string vBuildingMatrixUp, ref string dbGreenMatrix)
        {

            // building calculation
            string buildingFlagAndNr = null;
            string buildingFlagAndNrGreen = null;
            List<int> greenBuildingsId = edifici.GreenIdBuildings;

            List<int[,,]> listaArray = new List<int[,,]>();
            List<int[,,]> listaArrayGreen = new List<int[,,]>();

            foreach (Mesh m in edifici.Buildings)
            {
                try
                {
                    int index = edifici.Buildings.IndexOf(m) + 1;
                    int[,,] grid3d = myGrid.BasePoints(m, index, tol, ref buildingFlagAndNr);
                    listaArray.Add(grid3d);
                }
                catch
                {
                    continue;
                }
            }

            /*
                GREENINGS
            */
            if (greenBuildingsId != null)
            {

                int count = 1;
                foreach (int index in greenBuildingsId)
                {
                    int[,,] grid3d = myGrid.BasePoints(edifici.Buildings[index], count, tol, ref buildingFlagAndNrGreen);
                    listaArrayGreen.Add(grid3d);
                    count += 1;
                }
                // green
                int[,,] integerGreen = myGrid.mergeMatrix(listaArrayGreen);
                dbGreenMatrix = edifici.GreenSparseMatrix(integerGreen);
            }

            // make materials
            // preparation and delegate
            int[,,] integerMatrix = myGrid.mergeMatrix(listaArray);
            dbMatrix = edifici.NormalSparseMatrix(integerMatrix);

            // 2d matrix
            envimetGrid.BuildingMatrix.BuildingMatrix2d matrix2d = edifici.BuildingId2d;
            int[,] buildingId2d = matrix2d(integerMatrix);

            matrix2d = edifici.BuildingBottom2d;
            int[,] buildingBottom2d = matrix2d(integerMatrix);

            matrix2d = edifici.BuildingTop2d;
            int[,] buildingTop2d = matrix2d(integerMatrix);

            // static method for visualization / string parsing
            vBuildingMatrixId = envimetGrid.AutoGrid.View2dMatrix(buildingId2d);
            vBuildingMatrixBottom = envimetGrid.AutoGrid.View2dMatrix(buildingBottom2d);
            vBuildingMatrixUp = envimetGrid.AutoGrid.View2dMatrix(buildingTop2d);

            return buildingFlagAndNr;

        }

        // WRITER

        static public void INXwriteMethod(
          string path,
          envimetGrid.AutoGrid grid,
          envimetGrid.NestingGrid nestingGrid,
          envimentIntegration.LocationFromLB location,
          envimetGrid.BuildingMatrix building,
          envimetGrid.Element2dMatrix simpleplants2D,
          envimetGrid.Element2dMatrix soils2D,
          envimetGrid.Element2dMatrix sources2D,
          envimetGrid.ThreeDimensionalPlants plants3D
          )
        {

            // preparation
            var now = DateTime.Now;
            string revisionDate = now.ToString("yyyy-MM-dd HH:mm:ss");
            double tol = 0.0001;
            string emptyMatrixNull = "\n" + envimetGrid.AutoGrid.EmptyMatrix("");
            string emptyMatrixZero = "\n" + envimetGrid.AutoGrid.EmptyMatrix("0");

            string emptyMatrixSoil = "\n" + envimetGrid.AutoGrid.EmptyMatrix("000000");

            string dbMatrix = null;
            string dbGreenMatrix = null;

            string vBuildingMatrixId = null;
            string vBuildingMatrixBottom = null;
            string vBuildingMatrixUp = null;


            // calculation
            string buildingFlagAndNr = WriteINX.BuildingCalculation(building, grid, tol, ref dbMatrix, ref vBuildingMatrixId, ref vBuildingMatrixBottom, ref vBuildingMatrixUp, ref dbGreenMatrix);

            string ID_plants1D = null;
            if (simpleplants2D != null)
            {
                ID_plants1D = "\n" + WriteINX.Element2dCalculation(simpleplants2D, grid, tol);
            }
            else
            {
                ID_plants1D = emptyMatrixNull;
            }

            string ID_soilprofile = "\n" + WriteINX.Element2dCalculation(soils2D, grid, tol);

            string ID_sources = null;
            if (sources2D != null)
            {
                ID_sources = "\n" + WriteINX.Element2dCalculation(sources2D, grid, tol);
            }
            else
            {
                ID_sources = emptyMatrixNull;
            }

            // start with xml

            XmlTextWriter xWriter = new XmlTextWriter(path, Encoding.UTF8);
            xWriter.WriteStartElement("ENVI-MET_Datafile");
            xWriter.WriteString("\n ");

            string[] empty = { };

            // section Header
            string headerTitle = "Header";
            string[] headerTag = new string[] { "filetype", "version", "revisiondate", "remark", "encryptionlevel" };
            string[] headerValue = new string[] { "INPX ENVI-met Area Input File", "401", revisionDate, "Created with lb_envimet", "0" };

            WriteINX.xmlSection(xWriter, headerTitle, headerTag, headerValue, 0, empty);

            // section baseData
            string baseDataTitle = "baseData";
            string[] baseDataTag = new string[] { "modelDescription", "modelAuthor" };
            string[] baseDataValue = new string[] { " A brave new area ", " DragonFly envimet " };

            WriteINX.xmlSection(xWriter, baseDataTitle, baseDataTag, baseDataValue, 0, empty);

            // section modelGeometry
            // preparation telescope / splitted grid

            string useSplitting = null;
            string verticalStretch = null;
            string startStretch = null;
            string grids3DK = null;
            string gridsZ = null;
            string useTelescoping = null;
            string gridsI = (envimetGrid.AutoGrid.NumX + 1).ToString();
            string gridsJ = (envimetGrid.AutoGrid.NumY + 1).ToString();
            string[] attribute2dElements = { "matrix-data", gridsI, gridsJ };
            string dx = grid.DimX.ToString("n5");
            string dy = grid.DimY.ToString("n5");
            string dz = grid.DimZ.ToString("n5");

            if (grid.telescope.HasValue)
            {
                useTelescoping = "1";
                useSplitting = "0";
                verticalStretch = grid.telescope.ToString();
                startStretch = grid.StartTelescopeHeight.ToString();
                grids3DK = gridsZ = grid.ZGrids.ToString();
            }
            else
            {
                useTelescoping = "0";
                useSplitting = "1";
                verticalStretch = "0";
                startStretch = "0";
                gridsZ = (grid.ZGrids - 4).ToString();
                grids3DK = (grid.ZGrids).ToString();
            }

            string modelGeometryTitle = "modelGeometry";
            string[] modelGeometryTag = new string[] { "grids-I", "grids-J", "grids-Z", "dx", "dy", "dz-base", "useTelescoping_grid", "useSplitting", "verticalStretch", "startStretch", "has3DModel", "isFull3DDesign" };
            string[] modelGeometryValue = new string[] { gridsI, gridsJ, gridsZ, dx, dy, dz, useTelescoping, useSplitting, verticalStretch, startStretch, "1", "1" };

            WriteINX.xmlSection(xWriter, modelGeometryTitle, modelGeometryTag, modelGeometryValue, 0, empty);


            // section nestingArea
            string nestingAreaTitle = "nestingArea";
            string[] nestingAreaTag = new string[] { "numberNestinggrids", "soilProfileA", "soilProfileB" };
            string[] nestingAreaValue = new string[] { nestingGrid.NumNestingGrid.ToString(), nestingGrid.SoilProfileA, nestingGrid.SoilProfileB };

            WriteINX.xmlSection(xWriter, nestingAreaTitle, nestingAreaTag, nestingAreaValue, 0, empty);


            // section locationData
            string locationDataTitle = "locationData";
            string[] locationDataTag = new string[] { "modelRotation", "projectionSystem", "realworldLowerLeft_X", "realworldLowerLeft_Y", "locationName", "location_Longitude", "location_Latitude", "locationTimeZone_Name", "locationTimeZone_Longitude" };
            string[] locationDataValue = new string[] { location.ModelRotation.ToString("n5"), " ", " 0.00000 ", " 0.00000 ", location.LocationName, location.Longitude.ToString(), location.Latitude.ToString(), location.TimeZone, " 15.00000 " };

            WriteINX.xmlSection(xWriter, locationDataTitle, locationDataTag, locationDataValue, 0, empty);


            // section defaultSettings
            string defaultSettingsTitle = "defaultSettings";
            string[] defaultSettingsTag = new string[] { "commonWallMaterial", "commonRoofMaterial" };
            string[] defaultSettingsValue = new string[] { building.CommonWallMaterial, building.CommonRoofMaterial };

            WriteINX.xmlSection(xWriter, defaultSettingsTitle, defaultSettingsTag, defaultSettingsValue, 0, empty);


            // section buildings2D
            string buildings2DTitle = "buildings2D";
            string[] buildings2DTag = new string[] { "zTop", "zBottom", "buildingNr", "fixedheight" };
            string[] buildings2DValue = new string[] { "\n" + vBuildingMatrixUp, "\n" + vBuildingMatrixBottom, "\n" + vBuildingMatrixId, emptyMatrixZero };

            WriteINX.xmlSection(xWriter, buildings2DTitle, buildings2DTag, buildings2DValue, 1, attribute2dElements);


            // section simpleplants2D
            string simpleplants2DTitle = "simpleplants2D";
            string[] simpleplants2DTag = new string[] { "ID_plants1D" };
            string[] simpleplants2DValue = new string[] { ID_plants1D };

            WriteINX.xmlSection(xWriter, simpleplants2DTitle, simpleplants2DTag, simpleplants2DValue, 1, attribute2dElements);


            // section plant3d
            if (plants3D != null)
            {
                WriteINX.Three3dCalculation(plants3D, grid, tol);

                for (int i = 0; i < plants3D.PropertiesTree.Count; i++)
                {

                    string plants3DTitle = "3Dplants";
                    string[] plants3DTag = new string[] { "rootcell_i", "rootcell_j", "rootcell_k", "plantID", "name", "observe" };
                    string[] plants3DValue = new string[] { plants3D.PropertiesTree[i][0], plants3D.PropertiesTree[i][1], plants3D.PropertiesTree[i][2], plants3D.PropertiesTree[i][3], plants3D.PropertiesTree[i][4], plants3D.PropertiesTree[i][5] };

                    WriteINX.xmlSection(xWriter, plants3DTitle, plants3DTag, plants3DValue, 0, empty);
                }
            }


            // section soils2D
            string soils2DTitle = "soils2D";
            string[] soils2DTag = new string[] { "ID_soilprofile" };
            string[] soils2DValue = new string[] { ID_soilprofile };

            WriteINX.xmlSection(xWriter, soils2DTitle, soils2DTag, soils2DValue, 1, attribute2dElements);


            // section dem (next release)
            string demTitle = "dem";
            string[] demDTag = new string[] { "terrainheight" };
            string[] demValue = new string[] { emptyMatrixZero };

            WriteINX.xmlSection(xWriter, demTitle, demDTag, demValue, 1, attribute2dElements);


            // section sources2D
            string sources2DTitle = "sources2D";
            string[] sources2DTag = new string[] { "ID_sources" };
            string[] sources2DValue = new string[] { ID_sources };

            WriteINX.xmlSection(xWriter, sources2DTitle, sources2DTag, sources2DValue, 1, attribute2dElements);


            // section receptors2D (next release)
            string receptors2DTitle = "receptors2D";
            string[] receptors2DTag = new string[] { "ID_receptors" };
            string[] receptors2DValue = new string[] { emptyMatrixNull };

            WriteINX.xmlSection(xWriter, receptors2DTitle, receptors2DTag, receptors2DValue, 1, attribute2dElements);


            // section additionalData (maybe next release)
            string additionalDataTitle = "additionalData";
            string[] additionalDataTag = new string[] { "db_link_point", "db_link_area" };
            string[] additionalDataValue = new string[] { emptyMatrixNull, emptyMatrixNull };

            WriteINX.xmlSection(xWriter, additionalDataTitle, additionalDataTag, additionalDataValue, 1, attribute2dElements);

            // section greenins part 1
            /////////////////////////////////////////
            if (building.GreenIdBuildings.Count > 0)
            {
                for (int i = 0; i < building.GreenIdBuildings.Count; i++)
                {

                    string buildinginfoTitle = "Buildinginfo";
                    string[] buildinginfoTag = new string[] { "BuildingInternalNr", "BuildingName", "BuildingWallMaterial", "BuildingRoofMaterial", "BuildingFacadeGreening", "BuildingRoofGreening" };
                    string[] buildinginfoValue = new string[] { (building.GreenIdBuildings[i] + 1).ToString(), " ", building.selectedWallMaterialGreenings[i], building.selectedRoofMaterialGreenings[i], building.greenWallMaterial[i], building.greenRoofMaterial[i] };

                    WriteINX.xmlSection(xWriter, buildinginfoTitle, buildinginfoTag, buildinginfoValue, 0, empty);
                }
            }


            // section modelGeometry3D
            // preparation
            string grids3D_I = gridsI;
            string grids3D_J = gridsJ;
            string grids3D_K = grids3DK;
            string[] attribute3dElementsBuilding = { "sparematrix-3D", gridsI, gridsJ, grids3DK, "0" };
            string[] attribute3dElementsTerrain = { "sparematrix-3D", gridsI, gridsJ, grids3DK, "0.00000" };
            string[] attribute3dElementsWallDB = { "sparematrix-3D", gridsI, gridsJ, grids3DK, "" };

            string modelGeometry3DTitle = "modelGeometry3D";
            string[] modelGeometry3DTag = new string[] { "grids3D-I", "grids3D-J", "grids3D-K" };
            string[] modelGeometry3DValue = new string[] { gridsI, gridsJ, grids3DK };

            WriteINX.xmlSection(xWriter, modelGeometry3DTitle, modelGeometry3DTag, modelGeometry3DValue, 0, empty);


            // section buildings3D
            string buildings3DTitle = "buildings3D";
            string[] buildings3DTag = new string[] { "buildingFlagAndNr" };
            string[] buildings3DValue = new string[] { "\n" + buildingFlagAndNr };

            WriteINX.xmlSection(xWriter, buildings3DTitle, buildings3DTag, buildings3DValue, 2, attribute3dElementsBuilding);


            // section dem3D (next release)
            string dem3DTitle = "dem3D";
            string[] dem3DTag = new string[] { "terrainflag" };
            string[] dem3DValue = new string[] { "\n" };

            WriteINX.xmlSection(xWriter, dem3DTitle, dem3DTag, dem3DValue, 2, attribute3dElementsTerrain);


            // section WallDB
            string WallDBTitle = "WallDB";
            string[] WallDBTag = new string[] { "ID_wallDB" };
            string[] WallDBValue = new string[] { "\n" + dbMatrix };

            WriteINX.xmlSection(xWriter, WallDBTitle, WallDBTag, WallDBValue, 2, attribute3dElementsWallDB);


            // section SingleWallDB (maybe next release)
            string SingleWallDBTitle = "SingleWallDB";
            string[] SingleWallDBTag = new string[] { "ID_singlewallDB" };
            string[] SingleWallDBValue = new string[] { "\n" };

            WriteINX.xmlSection(xWriter, SingleWallDBTitle, SingleWallDBTag, SingleWallDBValue, 2, attribute3dElementsWallDB);


            // section GreeningDB
            string GreeningDBTitle = "GreeningDB";
            string[] GreeningDBTag = new string[] { "ID_GreeningDB" };
            string[] GreeningDBValue = null;
            if (building.GreenIdBuildings.Count == 0)
            {
                GreeningDBValue = new string[] { " " };
            }
            else
            {
                GreeningDBValue = new string[] { "\n" + dbGreenMatrix };
            }

            WriteINX.xmlSection(xWriter, GreeningDBTitle, GreeningDBTag, GreeningDBValue, 2, attribute3dElementsWallDB);

            xWriter.WriteEndElement();
            xWriter.Close();
        }
    }


    public class ReadEnvimet
    {
        public string Metaname { get; set; }

        private string readEnvimetNoBinaryFile()
        {
            string characters = @"[^\s()_<>/,\.A-Za-z0-9=""]+";
            Encoding isoLatin1 = Encoding.GetEncoding(28591); ;
            string text = System.IO.File.ReadAllText(Metaname, isoLatin1);

            Regex.Replace(characters, "", text);

            return text.Replace("&", "").Replace("<Remark for this Source Type>", "");
        }

        public string writeReadebleEDXFile(string path, string variableName = "ENVI", string fileType = ".EDX")
        {
            string fileNameWithExtension = variableName + fileType;

            string newFile = System.IO.Path.Combine(path, fileNameWithExtension);

            // make a readible version of the xml file
            string metainfo = readEnvimetNoBinaryFile();

            // write file in a new destination
            System.IO.File.WriteAllText(newFile, metainfo);

            return newFile;
        }
    }
}

namespace envimetSimulationFile
{ 
    public class MainSettings
    {
        public string SimName { get; set; }
        public string INXfileAddress { get; set; }
        public string StartDate { get; set; }
        public string StartTime { get; set; }
        public int SimDuration { get; set; }
        public double WindSpeed { get; set; }
        public double WindDir { get; set; }
        public double Roughness { get; set; }
        public double InitialTemperature { get; set; }
        public double SpecificHumidity { get; set; }
        public double RelativeHumidity { get; set; }
    }


    public class SampleForcingSettings
    {
        private string temperature;
        private string relativeHumidity;
        private int totNumbers;

        public string Temperature { get { return temperature; } }
        public string RelativeHumidity { get { return relativeHumidity; } }
        public int TotNumbers { get { return totNumbers; } }

        public SampleForcingSettings(List<double> temperature, List<double> relativeHumidity)
        {
            this.temperature = String.Join(",", temperature);
            this.relativeHumidity = String.Join(",", relativeHumidity);
            this.totNumbers = temperature.Count;
        }
    }
}

/**********************************************************
  ENVI_MET Integration Location - LB
***********************************************************/
namespace envimentIntegration
{
    public class LocationFromLB
    {
        private string location;

        public string LocationName { get; }
        public string Latitude { get; }
        public string Longitude { get; }
        public string TimeZone { get; }
        public int ModelRotation { get; }

        public LocationFromLB(string location, int modelRotation)
        {
            this.location = location;
            this.ModelRotation = modelRotation;

            // split string
            string[] locationStr = location.Split('\n');
            string newLocStr = "";

            foreach (string line in locationStr)
            {
                string cLine;
                if (line.Contains("!"))
                {
                    cLine = line.Split('!')[0];
                    newLocStr = newLocStr + cLine.Replace(" ", "");
                }
                else
                {
                    newLocStr = newLocStr + line;
                    newLocStr = newLocStr.Replace(";", "");
                }
            }

            string[] locationInfo = newLocStr.Split(',');

            string locationName = locationInfo[1];
            double latitude = Convert.ToDouble(locationInfo[2]);
            double longitude = Convert.ToDouble(locationInfo[3]);
            string timeZone = locationInfo[4];

            string timeZoneEnvimet;

            // timezone
            double num = Convert.ToDouble(timeZone);
            if (num > 0)
            {
                timeZoneEnvimet = "UTC+" + Convert.ToString((int)num);
            }
            else if (num < 0)
            {
                timeZoneEnvimet = "UTC-" + Convert.ToString((int)num);
            }
            else
            {
                timeZoneEnvimet = "GMT";
            }

            // 6 digits
            this.LocationName = locationName;
            this.Latitude = latitude.ToString("n6");
            this.Longitude = longitude.ToString("n6");
            this.TimeZone = timeZoneEnvimet;

        }
    }
}
