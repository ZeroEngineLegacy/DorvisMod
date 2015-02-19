import Zero
import Events
import Property
import math
import DebugDraw
import Color
import random
import VectorMath

# Forward Declarations
Vec3 = VectorMath.Vec3;
Quat = VectorMath.Quat;

class DoodadPainter:
    Object0 = Property.Resource("Archetype");
    #Object1 = Property.Resource("Archetype");
    Radius = Property.Float(20.0);
    Density = Property.Float(0.0003);
    RayHeight = Property.Float(300);
    #MinScale = Property.Float(0.6);
    #MaxScale = Property.Float(1.0);
    ScaleCurve = Property.Resource("SampleCurve");
    DebugDrawResolution = Property.Uint(150);
    
    def Initialize(self, initializer):
        self.Reload();
        
    def Reload(self):
        self.PreviewObject = None;
        self.ShiftDown = False;
        #self.ObjectList = ["PalmTree", "PalmTree"];
        self.ObjectList = ["Rock1", "Rock2"];
        #self.ObjectList = [self.Object0, self.Object1];
     
    def GetWorldPosEvent(self, Viewport, MouseEvent):
        start = Viewport.GetPositionInWorldFromMouse(MouseEvent.Mouse);
        dir = Viewport.GetRayDirectionInWorldFromMouse(MouseEvent.Mouse);
        return self.GetWorldPos(start, dir, Viewport.TargetSpace);
        
    def GetWorldPosFromScreen(self, Viewport, mousePos):
        start = Viewport.GetPositionInWorldFromScreenPos(mousePos);
        dir = Viewport.GetRayDirectionInWorldFromScreenPos(mousePos);
        return self.GetWorldPos(start, dir, Viewport.TargetSpace);
        
    def GetWorldPos(self, start, dir, space):
        for CastResult in space.PhysicsSpace.CastRayResults(start, dir, 25):
            if (not CastResult.GetObjectHit().HeightMap):
            #if (CastResult.GetObjectHit().HeightMap == self.PreviewObject):
                continue;
                
            pos = CastResult.GetWorldPosition();
            return (True, pos);
        return (False, Vec3(0,0,0));
        
    def KeyDown(self, Viewport, KeyboardEvent):
        #print(KeyboardEvent.Key == Zero.Keys.D);
        if (KeyboardEvent.Key == Zero.Keys.Shift):
            self.ShiftDown = True;
        return False
    
    def KeyUp(self, Viewport, KeyboardEvent):
        if (KeyboardEvent.Key == Zero.Keys.Shift):
            self.ShiftDown = False;
        #print(KeyboardEvent.Key == Zero.Keys.D);
        return False; 
    
    def ShouldBeginManipulation(self, Viewport, KeyboardEvent):
        return False
     
    def MouseDown(self, Viewport, MouseEvent):
        self.Tool.BeginManipulation(Viewport);
        return True;
        ret = self.GetWorldPosEvent(Viewport, MouseEvent);
        if (ret[0]):
            pos = ret[1];
            
            space = Viewport.TargetSpace;
            self.Space = space;
            spawnPositions = self.GetSpawnPositions(pos);
            self.CreateAtPositions(spawnPositions);
            #space.CreateAtPosition("Tree_evergreen", pos);
            
        #self.BeginManipulation(Viewport);
        return True;
    
    def MouseDoubleClick(self, Viewport, MouseEvent):
        return True; 
    
    def RightMouseDown(self, Viewport, MouseEvent):
        return False;
    
    def MouseUp(self, Viewport, MouseEvent):
        return False;
        
    def RightMouseUp(self, Viewport, MouseEvent):
        return False;
        
    def MouseMoveOnViewport(self, Viewport, MouseEvent):
        space = Viewport.TargetSpace;
        ret = self.GetWorldPosEvent(Viewport, MouseEvent);
        if (ret[0]):
            pos = ret[1];
            #if (not self.PreviewObject):
                #self.PreviewObject = space.Create(self.Object0);
                #if (self.PreviewObject.Model):
                    #self.PreviewObject.Model.Visible = False;
                #self.PreviewObject.RemoveComponentByName("RigidBody");
                #self.PreviewObject.RemoveComponentByName("Collider");
            #self.PreviewObject.Transform.Translation = pos;
            self.LastPos = pos;
            self.LastSpace = space;
            return True
            
        if (self.PreviewObject):
            self.PreviewObject.Destroy();
            
       #return False
        
    def DrawCircle(self, center, radius, resolution, space):
        step = math.pi * 2.0 / resolution;
        curr = 0.0
        
        self.Points = []
        for i in range(0, resolution):
            pos = Vec3(math.cos(curr), 0, math.sin(curr)) * radius;
            pos += center;
            
            currPos = self.GetWorldPos(pos + Vec3(0,250,0), Vec3(0,-1,0), space)[1];
            self.Points.append(currPos);
            curr += step;
        
        for i in range(0, resolution):
            p0 = self.Points[i];
            p1 = self.Points[(i + 1) % resolution];
            
            DebugDraw.DrawLine(start = p0 + Vec3(0,0.03,0), end = p1 + Vec3(0,0.03,0), 
                               # Below are optional
                               color = Color.Red, 
                               duration = 0.0, 
                               onTop = False);
        
    def FocusLost(self, Viewport, FocusEvent):
        if (self.PreviewObject):
            self.PreviewObject.Destroy();
        
    def Activate(self):
        print("Activate");
        
    def Deactivate(self):
        if (self.PreviewObject):
            self.PreviewObject.Destroy();
        
    def Draw(self):
        #if (self.PreviewObject):
        self.DrawCircle(self.LastPos, self.Radius, self.DebugDrawResolution, self.LastSpace);
        return;
        
    def MouseScroll(self, Viewport, MouseEvent):
        #print("Scroll")
        if (self.ShiftDown):
            self.Radius -= MouseEvent.Scroll.y;
            return True;
        return False
        
    def StartDrag(self, mouseStart, Viewport):
        print("StartDrag");
        
    def EndDrag(self, Viewport):
        print("EndDrag");
        
    def MouseMovementDrag(self, mouseStart, newPosition, Viewport):
        print("MouseMove");
        pos = self.GetWorldPosFromScreen(Viewport, newPosition)[1];
        space = Viewport.TargetSpace;
        self.Space = space;
        spawnPositions = self.GetSpawnPositions(pos);
        self.CreateAtPositions(spawnPositions);
        return True;
        
    def GetSpawnPositions(self, center):
        area = math.pi * self.Radius * self.Radius;
        doodadCount = int(area * self.Density);
        if (doodadCount <= 0):
            doodadCount = 1;
        spawnPositions = [];
        
        for n in range(0, doodadCount):
            rayStart = Vec3(0,0,0);
            rayStart.x += random.uniform(-self.Radius, +self.Radius);
            rayStart.z += random.uniform(-self.Radius, +self.Radius);
            
            if (rayStart.length() > self.Radius):
                n-=1;
                continue
            
            rayStart += center + Vec3(0, self.RayHeight, 0);
            
            CastResults = self.Space.PhysicsSpace.CastRayResults(rayStart, Vec3(0,-1,0), 25);
            for CastResult in CastResults:
                objectHit = CastResult.GetObjectHit();
                
                # Continue if it wasn't the height map
                if (not objectHit.HeightMap or objectHit.DoNotSpawnOn):
                    n -= 1;
                    continue
                     
                pos = CastResult.GetWorldPosition();
                normal = CastResult.GetNormal();
                spawnPositions.append((pos, normal));
              
        return spawnPositions;
        
    def CreateAtPositions(self, spawnPositions):
        root = self.Space.FindObjectByName("TestTrees");
        if (not root):
            root = self.Space.CreateAtPosition("Transform", Vec3(0,0,0));
            root.Name = "TestTrees";
             
        for entry in spawnPositions:
            pos = entry[0];
            normal = entry[1];
            obj = self.SpawnDoodad(pos, normal);
            obj.AttachToRelative(root);
            
    def SpawnDoodad(self, pos, normal):
            normal = normal.lerp(Vec3(0,1,0), 0.7).normalized();
            objectToSpawn = self.ObjectList[random.randint(0,len(self.ObjectList) - 1)];
            print("----------------------------------- ", objectToSpawn);
            archetype = self.Space.Create(objectToSpawn);
            archetype.Transform.Translation = pos;
            right = normal.cross(Vec3(1,0,0));
            rotation = Quat.EulerXYZ(0, random.uniform(0, math.pi * 2), 0);
            right = Quat.RotateVector(rotation, right)
            archetype.Transform.SetRotationUp(right, normal);
            
            SampleCurve = Zero.GetResource(self.ScaleCurve);
            t = random.uniform(0.0, 1.0);
            s = SampleCurve.Sample(t);
            
            archetype.Transform.Scale = Vec3(s, s, s);
            return archetype;
        
Zero.RegisterTool("DoodadPainter", DoodadPainter)