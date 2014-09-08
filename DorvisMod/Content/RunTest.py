import Zero
import Events
import VectorMath
import Action

class RunTest:
    def Initialize(self):
        if(Zero.Environment.GetParsedArgument("RunTest")):
            self.RunCommand(Zero.Editor)
    
    def Execute(self, Editor):
        self.RunCommand(Editor)
        
    def RunCommand(self, Editor):
        seq = Action.Sequence(Editor.Actions)
        Action.Delay(seq, 1.0)
        Action.Call(seq, self.PlayGame)
        Action.Delay(seq, 5.0)
        Action.Call(seq, Zero.Engine.Terminate)
        
    def PlayGame(self):
        Zero.Editor.ExecuteCommand("PlayGame")

Zero.RegisterCommand("RunTest", RunTest)