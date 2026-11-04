// Synthetic public-API feasibility fixture, not a backend or OTP implementation.
#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
#include <iterator>
#include <map>
#include <memory>
#include <mutex>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
#include "InterfacePassHelper.h"
#include "GpgIdManage.h"

namespace fs = std::filesystem;
static std::string bytes(const fs::path &path) {
    std::ifstream stream(path, std::ios::binary);
    if (!stream) throw std::runtime_error("fixture-read-failed");
    return std::string(std::istreambuf_iterator<char>(stream), std::istreambuf_iterator<char>());
}
static std::size_t leftovers(const fs::path &target) {
    std::size_t count = 0;
    for (const auto &item : fs::directory_iterator(target.parent_path())) {
        const auto name = item.path().filename().string();
        const auto prefix = target.filename().string();
        if (name != prefix && name.rfind(prefix, 0) == 0) ++count;
    }
    return count;
}
int main(int argc, char **argv) {
    // Opt-in SDK fixture; existing crypto modes remain unchanged.
    if (argc == 3 && std::string(argv[1]) == "disabled-gpg-selection") {
        bool before = false, after = false, rnp_access = false;
        try {
            auto prompt = [](RnpLoginRequestException &) { return false; };
            try { getInterfacePassHelper(false, argv[2], prompt); }
            catch (const std::invalid_argument &) { before = true; }
            auto *first = getInterfacePassHelper(true, argv[2], prompt);
            try { getInterfacePassHelper(false, argv[2], prompt); }
            catch (const std::invalid_argument &) { after = true; }
            rnp_access = first && getInterfacePassHelper(true, argv[2], prompt) == first;
        } catch (...) {
            // Unexpected exceptions never count as disabled-backend refusal.
        }
        const bool passed = before && after && rnp_access;
        std::cout << "{\"status\":\"" << (passed ? "pass" : "fail")
                  << "\",\"checks\":{\"reject-before-rnp\":" << (before ? "true" : "false")
                  << ",\"reject-after-rnp\":" << (after ? "true" : "false")
                  << ",\"rnp-access-after-rejection\":" << (rnp_access ? "true" : "false")
                  << "}}\n";
        return passed ? 0 : 1;
    }
    // mode, native home, store, original text, updated text, A keyid, B keyid.
    if (argc != 8) return 2;
    std::map<std::string, bool> checks;
    std::map<std::string, std::size_t> observations;
    std::size_t password_calls = 0, prompt_calls = 0, save_calls = 0;
    const char *expect_flag = std::getenv("FIXTURE_EXPECT_CORRECTIONS");
    const bool expect_corrections = expect_flag && std::string(expect_flag) == "1";
    const char *stage = "fixture-initialization";
    const char *exception_kind = "none";
    bool error = false;
    try {
        const std::string mode = argv[1], home = argv[2];
        const fs::path store = argv[3];
        const std::string original_text = bytes(argv[4]), updated_text = bytes(argv[5]);
        const std::string key_a = argv[6], key_b = argv[7];
        if (mode != "refuse" && mode != "normal" && mode != "read-b") return 2;
        const char *fd = std::getenv("FIXTURE_PASSWORD_FD");
        if (!fd || std::string(fd).find_first_not_of("0123456789") != std::string::npos)
            throw std::runtime_error("missing-fixture-fd");
        std::ifstream password_stream(std::string("/proc/self/fd/") + fd);
        std::string password;
        if (!std::getline(password_stream, password)) throw std::runtime_error("fixture-fd-read-failed");
        auto prompt = [&](RnpLoginRequestException &) { ++prompt_calls; return false; };
        // A process gets one home/callback set: never switch singleton context.
        stage = "helper-construction";
        auto *helper = getInterfacePassHelper(true, home, prompt);
        helper->setPasswordCallback([&](std::string) {
            ++password_calls;
            return mode == "refuse" ? std::string{} : password;
        });
        if (mode == "refuse") {
            const auto target = store / "plain.gpg";
            const auto before = bytes(target);
            auto entry = helper->getPassFile(target.string());
            bool refused = false;
            try {
                entry->decrypt();
                ++save_calls;
                // Unexpected auth success is measured, not hidden by fake refusal.
                entry->encrypt(updated_text, {key_a}, false);
            } catch (const RnpLoginRequestException &) { refused = true; }
            checks["fresh-auth-refusal"] = refused && password_calls > 0 && prompt_calls > 0;
            checks["refusal-no-save"] = save_calls == 0 && bytes(target) == before;
        } else if (mode == "read-b") {
            for (const auto &name : {"nested/item.gpg", "multi/item.gpg"}) {
                auto entry = helper->getPassFile((store / name).string());
                entry->decrypt();
                checks[std::string("independent-b-") + name] = entry->getDecrypted() == updated_text;
            }
            checks["b-auth-callback"] = password_calls > 0 && prompt_calls == 0;
        } else {
            stage = "path-list-find";
            std::set<std::string> paths;
            std::map<std::string, std::string> unused_cache;
            helper->searchDown(store.string(), ".*", "", false, {}, {}, false, unused_cache,
                [&](std::string path) {
                    if (helper->isGpgFile(path)) paths.insert(fs::relative(path, store).generic_string());
                });
            checks["public-path-only-list"] = paths == std::set<std::string>{
                "plain.gpg", "inherited/item.gpg", "nested/item.gpg", "multi/item.gpg",
                "guard/item.gpg", "missing.gpg"};
            std::set<std::string> found;
            helper->searchDown(store.string(), "nested/.*", "", false, {}, {}, false, unused_cache,
                [&](std::string path) {
                    if (helper->isGpgFile(path)) found.insert(fs::relative(path, store).generic_string());
                });
            checks["public-path-only-find"] = found == std::set<std::string>{"nested/item.gpg"};
            checks["list-no-authentication"] = password_calls == 0 && prompt_calls == 0;
            auto entry = helper->getPassFile((store / "plain.gpg").string());
            stage = "public-decrypt";
            entry->decrypt();
            checks["public-decrypt-exact"] = entry->getDecrypted() == original_text;
            stage = "policy-locator-counts";
            const char *fingerprint = std::getenv("FIXTURE_A_FINGERPRINT");
            if (!fingerprint) throw std::runtime_error("missing-fixture-fingerprint");
            observations["fixture-keyid-list-count"] = helper->listKeys(key_a).size();
            observations["fixture-fingerprint-list-count"] = helper->listKeys(fingerprint).size();
            if (expect_corrections) {
                checks["corrected-fingerprint-lookup"] = observations["fixture-keyid-list-count"] == 1 &&
                    observations["fixture-fingerprint-list-count"] == 1;
            }
            for (const auto &relative : {"plain.gpg", "inherited/item.gpg", "nested/item.gpg", "multi/item.gpg"}) {
                const auto target = store / relative;
                // Public construction invokes its private init() unchanged.
                stage = "policy-construction";
                GpgIdManage policy(target.string(), store.string(), true, home, prompt);
                observations["policy-all-public-count"] = policy.allKeys.size();
                observations["policy-all-private-count"] = policy.allPrivateKeys.size();
                observations["policy-known-count"] = policy.keysFoundInGpgIdFile.size();
                observations["policy-unresolved-count"] = policy.keysNotFoundInGpgIdFile.size();
                observations["policy-recipient-count"] = policy.encryptTo.size();
                stage = "policy-validation";
                policy.ensureValidGpgIdFile();
                const std::set<std::string> recipients(policy.encryptTo.begin(), policy.encryptTo.end());
                const std::string name = relative;
                const auto expected = name.rfind("nested/", 0) == 0 ? std::set<std::string>{key_b} :
                    name.rfind("multi/", 0) == 0 ? std::set<std::string>{key_a, key_b} : std::set<std::string>{key_a};
                checks["policy-" + name] = recipients == expected;
                if (recipients != expected) throw std::runtime_error("policy-fixture-mismatch");
                auto file = helper->getPassFile(target.string());
                stage = "public-save";
                ++save_calls;
                file->encrypt(updated_text, policy.encryptTo, false);
                checks["successful-save-cache-" + name] = file->getDecrypted() == updated_text;
            }
            const auto guard_target = store / "guard/item.gpg";
            const auto guard_before = bytes(guard_target);
            bool guard_refused = false, guard_saved = false;
            try {
                GpgIdManage policy(guard_target.string(), store.string(), true, home, prompt);
                policy.ensureValidGpgIdFile();
                guard_saved = true;
                ++save_calls;
                helper->getPassFile(guard_target.string())->encrypt(updated_text, policy.encryptTo, false);
            } catch (const std::exception &) { guard_refused = true; }
            checks["unresolved-policy-no-save"] = guard_refused && !guard_saved && bytes(guard_target) == guard_before;
            const auto missing_target = store / "missing.gpg";
            const auto missing_before = bytes(missing_target);
            auto missing_entry = helper->getPassFile(missing_target.string());
            // Prime cache from a real decrypt, rather than assigning fixture state.
            missing_entry->decrypt();
            checks["failed-save-cache-primed"] = missing_entry->getDecrypted() == original_text;
            // The previous all-zero keyid was a native wildcard. This explicit
            // nonzero negative fixture is independently checked by the runner
            // against all generated primary/subkey IDs and here against helper lookup.
            const std::string absent_keyid = "DEADBEEFDEADBEEF";
            const auto absent_matches = helper->listKeys(absent_keyid).size();
            observations["absent-keyid-helper-list-count"] = absent_matches;
            if (absent_keyid == key_a || absent_keyid == key_b || absent_matches != 0)
                throw std::runtime_error("negative-fixture-key-present");
            bool missing_failed = false;
            try {
                ++save_calls;
                missing_entry->encrypt(updated_text, {absent_keyid}, false);
            } catch (const std::exception &) { missing_failed = true; }
            observations["missing-case-exception"] = missing_failed;
            observations["missing-case-target-exists"] = fs::exists(missing_target);
            observations["missing-case-original-ciphertext-equal"] = fs::exists(missing_target) && bytes(missing_target) == missing_before;
            observations["missing-recipient-leftovers"] = leftovers(missing_target);
            observations["failed-save-cache-has-new-text"] = missing_entry->getDecrypted() == updated_text;
            observations["failed-save-cache-preserves-old-text"] = missing_entry->getDecrypted() == original_text;
            if (expect_corrections) {
                checks["corrected-failed-save-cache"] = observations["failed-save-cache-preserves-old-text"];
            }
            checks["public-save-missing-recipient-preserves"] = missing_failed && observations["missing-case-original-ciphertext-equal"];
            // Naturally conflicting directory: exception/leftover evidence only,
            // not a rename failure over an existing encrypted file.
            const auto conflict = store / "conflict.gpg";
            fs::create_directory(conflict);
            { std::ofstream marker(conflict / "marker"); marker << "synthetic"; }
            auto conflict_entry = helper->getPassFile(conflict.string());
            checks["rename-conflict-cache-initially-empty"] = conflict_entry->getDecrypted().empty();
            bool rename_failed = false;
            try {
                ++save_calls;
                conflict_entry->encrypt(updated_text, {key_a}, false);
            } catch (const fs::filesystem_error &) { rename_failed = true; }
            observations["rename-conflict-leftovers"] = leftovers(conflict);
            observations["rename-conflict-cache-still-empty"] = conflict_entry->getDecrypted().empty();
            checks["rename-conflict-reported"] = rename_failed && bytes(conflict / "marker") == "synthetic";
            if (expect_corrections) {
                checks["corrected-rename-conflict-cleanup"] = observations["rename-conflict-leftovers"] == 0;
                checks["corrected-rename-conflict-cache"] = observations["rename-conflict-cache-still-empty"];
            }
            checks["normal-auth-callback"] = password_calls > 0 && prompt_calls == 0;
        }
        stage = "completed";
    } catch (const RnpLoginRequestException &) {
        error = true; exception_kind = "rnp-login-request";
    } catch (const fs::filesystem_error &) {
        error = true; exception_kind = "filesystem-error";
    } catch (const std::logic_error &) {
        error = true; exception_kind = "std-logic-error";
    } catch (const std::runtime_error &) {
        error = true; exception_kind = "std-runtime-error";
    } catch (const std::exception &) {
        error = true; exception_kind = "std-exception";
    } catch (...) {
        error = true; exception_kind = "unknown";
    }
    bool passed = !error && !checks.empty();
    for (const auto &check : checks) passed = passed && check.second;
    std::cout << "{\"status\":\"" << (passed ? "pass" : "fail") << "\",\"exception\":" << (error ? "true" : "false")
              << ",\"expect_corrections\":" << (expect_corrections ? "true" : "false")
              << ",\"stage\":\"" << stage << "\",\"exception_kind\":\"" << exception_kind << '"'
              << ",\"password_callbacks\":" << password_calls << ",\"login_prompts\":" << prompt_calls
              << ",\"save_calls\":" << save_calls << ",\"checks\":{";
    bool first = true;
    for (const auto &check : checks) {
        if (!first) std::cout << ',';
        first = false;
        std::cout << '"' << check.first << "\":" << (check.second ? "true" : "false");
    }
    std::cout << "},\"observations\":{";
    first = true;
    for (const auto &item : observations) {
        if (!first) std::cout << ',';
        first = false;
        std::cout << '"' << item.first << "\":" << item.second;
    }
    std::cout << "}}\n";
    return passed ? 0 : 1;
}
