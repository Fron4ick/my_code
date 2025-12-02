using System.Collections.Generic;

namespace Assembler
{

    public class SymbolAnalyzer
    {
        /// <summary>
        /// Находит все метки в ассемблерном коде, удаляет их из кода и вносит их адреса в таблицу символов.
        /// </summary>
        /// <param name="instructionsWithLabels">Ассемблерный код, возможно, содержащий метки</param>
        /// <param name="instructionsWithoutLabels">Ассемблерный код без меток</param>
        /// <returns>
        /// Таблица символов, содержащая все стандартные предопределенные символы (R0−R15, SCREEN, ...),
        /// а также все найденные в программе метки.
        /// </returns>
        public Dictionary<string, int> CreateSymbolsTable(string[] instructionsWithLabels,
            out string[] instructionsWithoutLabels)
        {
            throw new NotImplementedException();
        }
    }
}
