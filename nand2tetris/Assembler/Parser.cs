namespace Assembler
{
    using System.Collections.Generic;
    using System.Linq;

    public class Parser
    {
        public string[] RemoveWhitespacesAndComments(string[] asmLines)
        {
            return asmLines
                .Select(StripCommentBlock)
                .Select(NormalizeWhitespace)
                .Where(IsSignificantLine)
                .ToArray();
        }

        private string StripCommentBlock(string sourceLine)
        {
            var markerIndex = sourceLine.IndexOf("//");
            return markerIndex >= 0 
                ? sourceLine.Substring(0, markerIndex) 
                : sourceLine;
        }

        private string NormalizeWhitespace(string codeFragment)
        {
            return codeFragment.Replace(" ", "")
                              .Replace("\t", "");
        }

        private bool IsSignificantLine(string processedLine)
        {
            return processedLine.Length > 0;
        }
    }
}
