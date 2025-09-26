#include <bits/stdc++.h>
using namespace std;
using u16 = uint16_t;
using u64 = uint64_t;

static const int NUM_INPUTS = 4;   // in, s2, s1, s0
static const int NUM_OUTPUTS = 8;  // a..h
static const u16 FULL_MASK = 0xFFFF; // lower 16 bits used

// Global data filled from table
u16 target_out[NUM_OUTPUTS]; // target 16-bit vectors for outputs a..h
bool table_loaded = false;

// Parameters
int MAX_NANDS_GLOBAL = 12; // default, can be set up to 50 by user

// Progress reporting
volatile u64 tried_gate_configs = 0;
u64 report_interval = 10000;

// Solution storage
struct Solution {
    int g;
    vector<pair<int,int>> nand_inputs; // for each nand: (a_idx, b_idx)
    vector<int> outputs_assign; // size NUM_OUTPUTS: index of source signal
};
bool found_solution = false;
Solution solution;

// Helper: trim
static inline std::string trim(const std::string &s) {
    size_t a = s.find_first_not_of(" \t\r\n");
    if (a==string::npos) return "";
    size_t b = s.find_last_not_of(" \t\r\n");
    return s.substr(a, b-a+1);
}

// Parse input table: read either from file or stdin until EOF or blank line after at least one data row.
// Expected data rows: lines like "0,0,0,0;0,0,0,0,0,0,0,0;" (inputs;outputs;)
bool parse_table_from_stream(istream &in) {
    vector<string> lines;
    string line;
    while (std::getline(in, line)) {
        string t = trim(line);
        if (t.empty()) {
            // if we already read any lines, allow blank to end input
            if (!lines.empty()) break;
            else continue;
        }
        // skip header lines containing alpha
        bool has_alpha = false;
        for (char c : t) if (isalpha((unsigned char)c)) { has_alpha = true; break; }
        if (has_alpha) continue;
        lines.push_back(t);
    }
    if (lines.empty()) {
        cerr << "Нет строк таблицы в вводе.\n";
        return false;
    }
    // initialize targets
    for (int j=0;j<NUM_OUTPUTS;++j) target_out[j] = 0;
    vector<bool> seen(16,false);
    for (auto &ln : lines) {
        string s = ln;
        // replace ';' by '|' to split
        for (char &c : s) if (c==';') c='|';
        vector<string> parts;
        string cur;
        stringstream ss(s);
        while (getline(ss, cur, '|')) {
            cur = trim(cur);
            if (!cur.empty()) parts.push_back(cur);
        }
        if (parts.size() < 2) continue;
        // first part: four inputs (commas)
        vector<int> inbits;
        {
            stringstream si(parts[0]);
            string token;
            while (getline(si, token, ',')) {
                token = trim(token);
                if (token.empty()) continue;
                if (!(token=="0" || token=="1")) { inbits.clear(); break; }
                inbits.push_back(token=="1"?1:0);
            }
        }
        if (inbits.size() != NUM_INPUTS) continue;
        // second part: up to 8 outputs
        vector<int> outs;
        {
            stringstream so(parts[1]);
            string token;
            while (getline(so, token, ',')) {
                token = trim(token);
                if (token.empty()) continue;
                if (!(token=="0" || token=="1")) { outs.clear(); break; }
                outs.push_back(token=="1"?1:0);
            }
        }
        if (outs.size() < NUM_OUTPUTS) continue;
        // compute index
        int idx = (inbits[0]<<3) | (inbits[1]<<2) | (inbits[2]<<1) | (inbits[3]<<0); // in,s2,s1,s0
        seen[idx] = true;
        for (int j=0;j<NUM_OUTPUTS;++j) {
            if (outs[j]) target_out[j] |= (1u << idx);
        }
    }
    // check seen all 16 minterms
    for (int i=0;i<16;++i) if (!seen[i]) {
        cerr << "В таблице отсутствует строка с комбинацией индекса " << i << " (всего должно быть 16).\n";
        return false;
    }
    table_loaded = true;
    return true;
}

// Build initial input vectors (in, s2, s1, s0) as 16-bit masks
void build_input_vectors(array<u16,NUM_INPUTS> &invecs) {
    for (int i=0;i<16;++i) {
        int in = (i>>3)&1;
        int s2 = (i>>2)&1;
        int s1 = (i>>1)&1;
        int s0 = (i>>0)&1;
        if (in) invecs[0] |= (1u<<i);
        if (s2) invecs[1] |= (1u<<i);
        if (s1) invecs[2] |= (1u<<i);
        if (s0) invecs[3] |= (1u<<i);
    }
}

// Global for current search to avoid reallocation
int G_global;
u64 estimated_total_for_g = 0;

// compute estimated total combinations for given g (rough): product_{i=1..g} (num_sources)^2 * (num_signals_end)^NUM_OUTPUTS
// where num_sources for gate i = NUM_INPUTS + (i-1)
long double compute_estimated_total(int g) {
    long double prod = 1.0L;
    for (int i=1;i<=g;++i) {
        long double s = (long double)(NUM_INPUTS + (i-1));
        prod *= s*s;
    }
    long double end_signals = (long double)(NUM_INPUTS + g);
    for (int k=0;k<NUM_OUTPUTS;++k) prod *= end_signals;
    return prod;
}

// DFS: build gates connections. signals contains current signal vectors. fanout counts tracked.
// when reached all g gates, try assign outputs.
vector<u16> signals_global; // dynamic
vector<int> fanout_global;  // usage counts of signals (by selection of gate inputs earlier)
u64 local_tried_counter = 0;

void print_progress(int g) {
    if (estimated_total_for_g <= 0) return;
    long double percent = (long double)tried_gate_configs / (long double)estimated_total_for_g * 100.0L;
    if (percent > 100.0L) percent = 100.0L;
    cout << "\rПеребор с g="<<g<<". исследовано комбинаций вентилей: "<<tried_gate_configs
         << "    прибл. " << fixed << setprecision(5) << (double)percent << "%      " << flush;
}

// assignment of outputs: choose for each output one signal index with matching vector
vector<vector<int>> vector_to_indices; // map for current completed gates (index by target mask to list) -> we'll implement map by unordered_map of u16->vector<int>

// Build map from vector value -> indices
unordered_map<u16, vector<int>> vecmap_current;

bool try_assign_outputs_and_check_usage(int g, Solution &out_sol) {
    int total_signals = (int)signals_global.size(); // NUM_INPUTS + g
    // build vecmap
    vecmap_current.clear();
    for (int i=0;i<total_signals;++i) {
        vecmap_current[signals_global[i]].push_back(i);
    }
    // For each output j, check possible indices
    vector<vector<int>> choices(NUM_OUTPUTS);
    for (int j=0;j<NUM_OUTPUTS;++j) {
        auto it = vecmap_current.find(target_out[j]);
        if (it == vecmap_current.end()) return false; // no signal matches needed output
        choices[j] = it->second;
    }
    // We'll do recursive assignment with pruning of fanout limits and finally check that each input used >=1 and each nand output used >=1
    vector<int> assign(NUM_OUTPUTS, -1);
    // copy fanout array to modify with final outputs usage additions
    vector<int> fan = fanout_global;
    bool ok = false;
    function<void(int)> dfs_assign = [&](int pos) {
        if (found_solution) return;
        if (pos == NUM_OUTPUTS) {
            // after assignment, check inputs used at least once (indices 0..NUM_INPUTS-1)
            for (int i=0;i<NUM_INPUTS;++i) {
                if (fan[i] < 1) return;
            }
            // check that each nand output is used at least once: nand outputs are indices NUM_INPUTS..NUM_INPUTS+g-1
            for (int idx = NUM_INPUTS; idx < NUM_INPUTS + g; ++idx) {
                if (fan[idx] < 1) return;
            }
            // all ok, produce solution
            out_sol.g = g;
            // nand inputs in out_sol must be read from signals_global mapping; but we need to store selection - we capture via solution set in outer scope
            // we expect the calling code to have filled nand_inputs into out_sol already (we'll set before calling)
            out_sol.outputs_assign = assign;
            found_solution = true;
            ok = true;
            return;
        }
        // iterate candidate sources for output pos
        for (int idx : choices[pos]) {
            if (fan[idx] + 1 > 5) continue; // fanout limit
            // assign
            assign[pos] = idx;
            fan[idx] += 1;
            dfs_assign(pos+1);
            if (found_solution) return;
            fan[idx] -= 1;
            assign[pos] = -1;
        }
    };
    dfs_assign(0);
    return ok;
}

// store current nand inputs as solution candidate
vector<pair<int,int>> curr_nand_inputs;

void dfs_build_gates(int cur_gate, int g) {
    if (found_solution) return;
    if (cur_gate > g) {
        // one completed gate-configuration
        ++tried_gate_configs;
        // progress report occasionally
        if ((tried_gate_configs % report_interval) == 0) print_progress(g);
        // try assign outputs
        Solution cand;
        cand.g = g;
        cand.nand_inputs = curr_nand_inputs;
        bool ok = try_assign_outputs_and_check_usage(g, cand);
        if (ok) {
            // fill final solution with nand_inputs set earlier and outputs from try_assign...
            solution = cand;
            solution.nand_inputs = curr_nand_inputs;
            // print also final progress update
            print_progress(g);
        }
        return;
    }
    int total_signals_now = (int)signals_global.size();
    int remaining_gates = g - cur_gate + 1;
    // simple pruning: count how many inputs are still unused; can they be covered by remaining ports?
    int unused_inputs = 0;
    for (int i=0;i<NUM_INPUTS;++i) if (fanout_global[i] == 0) ++unused_inputs;
    if (unused_inputs > remaining_gates * 2) return; // impossible to cover all inputs -> prune

    // iterate over choices for a_idx and b_idx with symmetry: enforce a <= b
    for (int a = 0; a < total_signals_now; ++a) {
        if (fanout_global[a] + 1 > 5) continue;
        for (int b = a; b < total_signals_now; ++b) { // b from a to allow symmetry reduction
            if (fanout_global[b] + 1 > 5) continue;
            // apply
            fanout_global[a] += 1;
            fanout_global[b] += 1;
            u16 newvec = (u16)(~(signals_global[a] & signals_global[b]) & FULL_MASK);
            signals_global.push_back(newvec);
            fanout_global.push_back(0); // new signal initially unused
            curr_nand_inputs.emplace_back(a,b);
            // recurse
            dfs_build_gates(cur_gate+1, g);
            if (found_solution) return;
            // undo
            curr_nand_inputs.pop_back();
            signals_global.pop_back();
            fanout_global.pop_back();
            fanout_global[a] -= 1;
            fanout_global[b] -= 1;
        }
    }
}

int main(int argc, char** argv) {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    cout.setf(std::ios::fixed);
    cout<<setprecision(6);

    // read input table: from file if provided, else from stdin
    bool parsed = false;
    if (argc >= 2) {
        ifstream fin(argv[1]);
        if (!fin) {
            cerr << "Не удалось открыть файл " << argv[1] << "\n";
            return 1;
        }
        parsed = parse_table_from_stream(fin);
    } else {
        cout << "Вставьте строки таблицы истинности (по одной на строку), завершите пустой строкой или EOF:\n";
        parsed = parse_table_from_stream(cin);
    }
    if (!parsed) return 1;

    // ask max NAND
    int max_g = 0;
    cout << "Введите максимальное число NAND для перебора (рекомендуется <=20; максимум 50): ";
    string s;
    if (!getline(cin, s)) { cerr << "Ошибка чтения.\n"; return 1; }
    s = trim(s);
    if (s.empty()) {
        max_g = MAX_NANDS_GLOBAL;
    } else {
        try {
            max_g = stoi(s);
        } catch (...) { max_g = MAX_NANDS_GLOBAL; }
    }
    if (max_g < 0) max_g = 0;
    if (max_g > 50) max_g = 50;

    // prepare input vectors
    array<u16,NUM_INPUTS> invecs = {0,0,0,0};
    build_input_vectors(invecs);

    // initial signals: inputs in order in,s2,s1,s0 as user specified
    vector<u16> base_signals;
    base_signals.push_back(invecs[0]); // in
    base_signals.push_back(invecs[1]); // s2
    base_signals.push_back(invecs[2]); // s1
    base_signals.push_back(invecs[3]); // s0

    // iterate g from 0..max_g
    for (int g = 0; g <= max_g; ++g) {
        if (found_solution) break;
        cout << "\n=== Перебор с g = " << g << " ===\n";
        // prepare globals
        G_global = g;
        // estimate total
        long double est = compute_estimated_total(g);
        estimated_total_for_g = (u64) (est > 1e18 ? (u64)1e18 : (u64) est); // cap for safety
        // init signals_global and fanouts
        signals_global.clear(); signals_global.reserve(NUM_INPUTS + g + 2);
        fanout_global.clear(); fanout_global.reserve(NUM_INPUTS + g + 2);
        for (int i=0;i<NUM_INPUTS;++i) {
            signals_global.push_back(base_signals[i]);
            fanout_global.push_back(0);
        }
        // reset counters
        tried_gate_configs = 0;
        curr_nand_inputs.clear();
        curr_nand_inputs.reserve(g);
        // if g==0, directly try assign outputs w/o gates
        if (g == 0) {
            // build vecmap
            unordered_map<u16, vector<int>> vmap;
            for (int i=0;i<(int)signals_global.size();++i) vmap[signals_global[i]].push_back(i);
            bool possible = true;
            vector<vector<int>> choices(NUM_OUTPUTS);
            for (int j=0;j<NUM_OUTPUTS;++j) {
                auto it = vmap.find(target_out[j]);
                if (it == vmap.end()) { possible = false; break; }
                choices[j] = it->second;
            }
            if (possible) {
                // assign outputs simply try combinations (but typically few choices)
                vector<int> assign(NUM_OUTPUTS, -1);
                vector<int> fan = fanout_global;
                function<bool(int)> dfs0 = [&](int pos)->bool {
                    if (pos == NUM_OUTPUTS) {
                        // check inputs used >=1
                        for (int i=0;i<NUM_INPUTS;++i) if (fan[i] < 1) return false;
                        // no gate outputs to check
                        solution.g = 0;
                        solution.nand_inputs.clear();
                        solution.outputs_assign = assign;
                        found_solution = true;
                        return true;
                    }
                    for (int idx : choices[pos]) {
                        if (fan[idx] + 1 > 5) continue;
                        assign[pos] = idx;
                        fan[idx] += 1;
                        if (dfs0(pos+1)) return true;
                        fan[idx] -= 1;
                        assign[pos] = -1;
                    }
                    return false;
                };
                if (dfs0(0)) {
                    cout << "Найдена схема без NAND (g=0)!\n";
                    break;
                }
            }
            cout << "Нет решения при g=0.\n";
            continue;
        }
        // for g>=1, start DFS to build gates
        signals_global = vector<u16>(base_signals.begin(), base_signals.end());
        fanout_global = vector<int>(NUM_INPUTS, 0);
        curr_nand_inputs.clear();
        tried_gate_configs = 0;
        // choose reporting interval adaptively
        report_interval = 10000;
        dfs_build_gates(1, g);
        if (found_solution) break;
        cout << "\nЗавершён перебор g="<<g<<". исследовано комбинаций вентилей: "<<tried_gate_configs<<"\n";
    }

    if (!found_solution) {
        cout << "\nРешение не найдено для g <= " << max_g << ".\n";
        return 0;
    }

    // Print solution in requested format:
    cout << "\n\n=== НАЙДЕНА СХЕМА (минимальное число NAND = " << solution.g << ") ===\n";
    // header: n_1_a;n_1_b;...;a;b;...;h;
    for (int i=1;i<=solution.g;++i) {
        cout << "n_"<<i<<"_a;";
        cout << "n_"<<i<<"_b;";
    }
    cout << "a;b;c;d;e;f;g;h;\n";
    // second line: values (source names) for each field
    auto name_of = [&](int idx)->string {
        if (idx < 0) return string("?");
        if (idx < NUM_INPUTS) {
            if (idx==0) return string("in");
            if (idx==1) return string("s2");
            if (idx==2) return string("s1");
            if (idx==3) return string("s0");
        }
        // nand outputs numbered from NUM_INPUTS.. => map to n_1 etc
        int ni = idx - NUM_INPUTS + 1;
        return string("n_") + to_string(ni);
    };
    // print nand inputs
    for (int i=0;i<solution.g;++i) {
        int a = solution.nand_inputs[i].first;
        int b = solution.nand_inputs[i].second;
        cout << name_of(a) << ";";
        cout << name_of(b) << ";";
    }
    // print outputs assignments
    for (int j=0;j<NUM_OUTPUTS;++j) {
        cout << name_of(solution.outputs_assign[j]) << ";";
    }
    cout << "\n\nПодробности (индексы сигналов):\n";
    cout << "Сигналы: 0=in,1=s2,2=s1,3=s0, затем n_1..n_" << solution.g << "\n";
    cout << "NAND подключения (a,b) по индексам:\n";
    for (int i=0;i<solution.g;++i) {
        cout << "n_"<<i+1<<": ("<<solution.nand_inputs[i].first<<","<<solution.nand_inputs[i].second<<")\n";
    }
    cout << "Выходы a..h указывают на индексы:\n";
    for (int j=0;j<NUM_OUTPUTS;++j) {
        cout << char('a'+j)<<" -> "<<solution.outputs_assign[j]<<"\n";
    }
    cout << "\nГотово.\n";
    return 0;
}
