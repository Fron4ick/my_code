using System.Collections.Generic;
using System.Linq;

namespace Assembler
{
    public class SymbolAnalyzer
    {
        public Dictionary<string, int> CreateSymbolsTable(string[] sourceLines, out string[] cleanProgram)
        {
            var symbolTable = InitializePredefinedSymbols();
            var programBuffer = new List<string>();
            var instructionAddress = 0;

            foreach (var rawLine in sourceLines)
            {
                var token = rawLine.Trim();
                if (IsMeaninglessLine(token)) continue;
                
                if (TryRegisterLabel(token, instructionAddress, symbolTable))
                    continue;
                
                programBuffer.Add(token);
                instructionAddress++;
            }

            cleanProgram = programBuffer.ToArray();
            return symbolTable;
        }

        private Dictionary<string, int> InitializePredefinedSymbols()
        {
            var table = new Dictionary<string, int>();
            
            for (int i = 0; i <= 15; i++) 
            {
                table.Add($"R{i}", i);
            }
            
            table.Add("SP", 0); table.Add("LCL", 1);
            table.Add("ARG", 2); table.Add("THIS", 3);
            table.Add("THAT", 4);
            table.Add("SCREEN", 0x4000);
            table.Add("KBD", 0x6000);

            return table;
        }

        private bool TryRegisterLabel(string token, int address, Dictionary<string, int> table)
        {
            if (!IsLabelDeclaration(token)) return false;
            
            var label = ExtractLabelName(token);
            if (!table.ContainsKey(label)) table.Add(label, address);
            
            return true;
        }

        private bool IsMeaninglessLine(string token)
        {
            return token.Length == 0;
        }

        private bool IsLabelDeclaration(string instruction)
        {
            return instruction.StartsWith("(") && instruction.EndsWith(")");
        }

        private string ExtractLabelName(string labelToken)
        {
            return labelToken.Substring(1, labelToken.Length - 2);
        }
    }
}
