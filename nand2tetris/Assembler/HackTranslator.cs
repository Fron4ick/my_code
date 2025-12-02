using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Assembler
{
    public class HackTranslator
    {
        private int _variableAllocator = 16;

        private static readonly IReadOnlyDictionary<string, string> _compCodes = new Dictionary<string, string>
        {
            ["0"] = "0101010", ["1"] = "0111111", ["-1"] = "0111010",
            ["D"] = "0001100", ["A"] = "0110000", ["M"] = "1110000",
            ["!D"] = "0001101", ["!A"] = "0110001", ["!M"] = "1110001",
            ["-D"] = "0001111", ["-A"] = "0110011", ["-M"] = "1110011",
            ["D+1"] = "0011111", ["A+1"] = "0110111", ["M+1"] = "1110111",
            ["D-1"] = "0001110", ["A-1"] = "0110010", ["M-1"] = "1110010",
            ["D+A"] = "0000010", ["D+M"] = "1000010",
            ["D-A"] = "0010011", ["D-M"] = "1010011",
            ["A-D"] = "0000111", ["M-D"] = "1000111",
            ["D&A"] = "0000000", ["D&M"] = "1000000",
            ["D|A"] = "0010101", ["D|M"] = "1010101"
        };

        private static readonly IReadOnlyDictionary<string, string> _destCodes = new Dictionary<string, string>
        {
            ["null"] = "000", ["M"] = "001", ["D"] = "010", ["MD"] = "011",
            ["A"] = "100", ["AM"] = "101", ["AD"] = "110", ["AMD"] = "111"
        };

        private static readonly IReadOnlyDictionary<string, string> _jumpCodes = new Dictionary<string, string>
        {
            ["null"] = "000", ["JGT"] = "001", ["JEQ"] = "010", ["JGE"] = "011",
            ["JLT"] = "100", ["JNE"] = "101", ["JLE"] = "110", ["JMP"] = "111"
        };

        public string[] TranslateAsmToHack(string[] program, Dictionary<string, int> symbols) =>
            program.Select(line => line.StartsWith('@') 
                ? AInstructionToCode(line, symbols) 
                : CInstructionToCode(line))
            .ToArray();

        public string AInstructionToCode(string instruction, Dictionary<string, int> table) =>
            EncodeACommand(instruction, table);

        public string CInstructionToCode(string instruction) =>
            EncodeCCommand(instruction);

        private string EncodeACommand(string instruction, Dictionary<string, int> table)
        {
            var symbol = instruction.Substring(1);
            
            return int.TryParse(symbol, out var address) 
                ? ToBinary(address) 
                : ToBinary(GetOrCreateSymbol(symbol, table));
        }

        private int GetOrCreateSymbol(string symbol, Dictionary<string, int> table)
        {
            if (!table.TryGetValue(symbol, out var address))
            {
                address = _variableAllocator++;
                table.Add(symbol, address);
            }
            return address;
        }

        private string EncodeCCommand(string instruction)
        {
            var (comp, dest, jump) = ParseCommandParts(instruction);
            return $"111{_compCodes[comp]}{_destCodes[dest]}{_jumpCodes[jump]}";
        }

        private (string comp, string dest, string jump) ParseCommandParts(string instruction)
        {
            var jump = "null";
            var dest = "null";
            var comp = instruction;

            var semicolonPos = instruction.IndexOf(';');
            if (semicolonPos != -1)
            {
                jump = instruction.Substring(semicolonPos + 1);
                comp = instruction.Substring(0, semicolonPos);
            }

            var equalsPos = comp.IndexOf('=');
            if (equalsPos != -1)
            {
                dest = comp.Substring(0, equalsPos);
                comp = comp.Substring(equalsPos + 1);
            }

            return (comp, dest, jump);
        }

        private static string ToBinary(int value) => 
            Convert.ToString(value, 2).PadLeft(16, '0');
    }
}
