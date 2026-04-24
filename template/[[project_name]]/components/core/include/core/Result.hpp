#pragma once
#include <optional>
#include <type_traits>
#include <utility>
#include <variant>

namespace core {

// Minimal Result<T, E>. No exceptions. No heap. Use for fallible operations.
//
// INVARIANT — enforced by exceptions-off policy:
//   Callers MUST check is_ok() before value() and is_err() before error().
//   std::get on the wrong alternative would throw, but we compile with
//   CONFIG_COMPILER_CXX_EXCEPTIONS=n → UB. Reviewer agent rejects unchecked access.
template <typename T, typename E>
class [[nodiscard]] Result {
public:
    static Result Ok(T value) { return Result{std::in_place_index<0>, std::move(value)}; }
    static Result Err(E err) { return Result{std::in_place_index<1>, std::move(err)}; }

    bool is_ok() const { return v_.index() == 0; }
    bool is_err() const { return v_.index() == 1; }

    const T& value() const { return std::get<0>(v_); }
    const E& error() const { return std::get<1>(v_); }

private:
    template <std::size_t I, typename U>
    Result(std::in_place_index_t<I> tag, U&& u) : v_(tag, std::forward<U>(u)) {}
    std::variant<T, E> v_;
};

// Void specialization — stores E in std::optional so E is not required to be
// default-constructible. The earlier "Result{true, E{}}" design silently
// broke for any E that lacked a default constructor (common for struct
// errors with required fields).
template <typename E>
class [[nodiscard]] Result<void, E> {
public:
    static Result Ok() { return Result{std::nullopt}; }
    static Result Err(E e) { return Result{std::optional<E>{std::move(e)}}; }

    bool is_ok() const { return !err_.has_value(); }
    bool is_err() const { return err_.has_value(); }
    const E& error() const { return *err_; }

private:
    explicit Result(std::optional<E> e) : err_(std::move(e)) {}
    std::optional<E> err_;
};

}  // namespace core
