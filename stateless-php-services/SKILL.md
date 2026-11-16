---
name: stateless-php-services
description: Detect and refactor stateful services in PHP/Symfony projects to make them stateless. Use this skill whenever the user mentions stateful services, ResetInterface, service state leakage, long-running processes, RoadRunner, Swoole, FrankenPHP, or wants to make a PHP service stateless. Also trigger when analyzing service classes with setters, mutable private properties, or request-scoped state in Symfony services. Essential for code reviews touching service design, listener patterns, or middleware state.
---

# Stateless PHP Services

Detect and refactor stateful services in PHP/Symfony projects to eliminate ephemeral state from class properties.

## Why this matters

Stateful services store data that changes between method calls in class properties. This causes subtle bugs when:
- Switching to long-running process servers (RoadRunner, Swoole, FrankenPHP)
- Processing messages in queue workers
- Reusing service instances in loops or async contexts
- Scaling horizontally with shared service containers

Data from one request leaks into another. Users see wrong data. Payments charge wrong accounts. Logs show wrong correlation IDs.

## Three types of data in services

Only ephemeral state is problematic:

1. **Configuration** (safe): Immutable values set in constructor, often `readonly`. Defines base behavior. Does not change during execution.
2. **Dependencies** (safe): Other services injected via constructor. Tools for performing operations. Usually stateless themselves.
3. **Ephemeral state** (dangerous): Data that changes during operation, especially set via setters after construction or mutated during execution. This is request/call-specific data that should be passed as method parameters instead.

## Detection patterns

Search for these code smells in services (classes registered in the DI container, listeners, middleware, processors):

### Pattern 1: ResetInterface implementations
Any class implementing `Symfony\Contracts\Service\ResetInterface` holds request-scoped state that the container clears between requests via `reset()`. This is a **valid Symfony pattern** — not inherently bad — but it indicates the service is stateful and requires careful handling.

**When ResetInterface is appropriate:**
- The service must hold request-scoped state (e.g., current user, locale, correlation ID)
- Making it fully stateless would require invasive changes across many callers
- The application runs under PHP-FPM where Symfony's container reliably calls `reset()` after each request

**When ResetInterface becomes problematic:**
- Switching to long-running process servers (RoadRunner, Swoole, FrankenPHP) where `reset()` may not be called between requests
- Queue workers or async contexts where multiple messages are processed per process lifetime
- The `reset()` method is forgotten or bypassed in custom service instantiation

```php
class MyListener implements ResetInterface  // SIGNAL: holds request-scoped state
{
    private ?User $currentUser = null;
    
    public function setUser(?User $user): void { $this->currentUser = $user; }
    public function reset(): void { $this->currentUser = null; }  // Clears state between requests
}
```

**Decision tree:** Prefer making the service stateless when the refactor is small and safe. If full statelessness is impractical due to scope, risk, or cross-cutting concerns, `ResetInterface` is a **valid and legitimate solution** — not a hack. It is the Symfony-recommended pattern for request-scoped state and works reliably under PHP-FPM. In long-running or async contexts (RoadRunner, Swoole, FrankenPHP, queue workers), `ResetInterface` remains valid **only if** you verify `reset()` is called between every request/message. If you cannot guarantee `reset()` is invoked, then refactor to stateless.

### Pattern 2: Setter methods mutating service state
`public function set*(...)` methods on services that assign to private properties, especially when called from outside the class after construction.

Red flag setters:
- `setUser()`, `setAdminUser()`, `setCurrentUser()`
- `setRequest()`, `setContext()`
- `setLocale()`, `setDomain()`
- `setStamp()`, `setToken()`
- Any setter that stores call-specific data

```php
class OrderProcessor  // SMELL: service with setter
{
    private ?User $currentUser = null;  // SMELL: nullable property for ephemeral state
    
    public function setUser(User $user): void  // SMELL: setter for ephemeral state
    {
        $this->currentUser = $user;
    }
}
```

### Pattern 3: Nullable properties with deferred usage
Private properties initialized to `null` that get set in one method and read in another method later. The property acts as invisible parameter passing.

```php
class ReportGenerator  // SMELL: property used as hidden parameter
{
    private ?DateTime $reportDate = null;
    
    public function prepare(DateTime $date): void
    {
        $this->reportDate = $date;  // SMELL: storing for later
    }
    
    public function generate(): Report
    {
        return new Report($this->reportDate);  // SMELL: reading stored state
    }
}
```

### Pattern 4: State accumulation in loops or batch processing
Properties that get appended to rather than overwritten, especially in array properties or collections.

```php
class BatchProcessor  // SMELL: accumulating state
{
    private array $errors = [];  // SMELL: state grows over time
    
    public function processItem(Item $item): void
    {
        if (!$item->isValid()) {
            $this->errors[] = $item->getError();  // SMELL: accumulating across calls
        }
    }
}
```

### What is NOT a stateful service

Do not flag these:
- **Entities/Models**: Meant to hold state
- **DTOs/Value Objects**: Immutable or mutable data carriers
- **Form Types**: Symfony forms have their own lifecycle
- **Configuration properties**: `readonly` constructor-injected values
- **Dependency properties**: Other services injected via constructor
- **Caches**: Properties storing memoized computation results (idempotent)
- **Internal iterators/counters**: Properties used purely within a single method call scope

### False positives from automated tools

Tools like `igor-php` flag any class with mutable properties as "stateful". This produces false positives on Entities, Models, and DTOs.

**If you see Entities, DTOs, or Data Models in an audit report**, it usually means they are incorrectly registered as **shared services** in the Symfony DI container. Check your `services.yaml` autowiring configuration:

```yaml
# services.yaml — exclude data directories from autowiring
services:
    _defaults:
        autowire: true
        autoconfigure: true

    App\Domain\Model\:
        resource: '../src/Domain/Model'
        # These are entities — they should NOT be services
        # Remove this entry, or exclude the directory:
        exclude:
            - '../src/Domain/Model'
            - '../src/Domain/DTO'
```

Entities and DTOs belong in the domain layer, not in the DI container. Fix the autowiring configuration first to eliminate noise from your audit.

## Refactoring strategy

### Step 1: Identify the ephemeral state
Find all properties that store call-specific data. Ask: "Does this property's value depend on the current request/message/call?" If yes, it's ephemeral state.

### Step 2: Remove the property
Delete the private property that holds ephemeral state.

### Step 3: Remove the setter
Delete `set*()` methods that existed solely to populate the removed property.

### Step 4: Pass state as method parameters
Add the previously-stored data as parameters to the methods that actually need it.

```php
// BEFORE: Stateful
class OrderProcessor
{
    private ?User $currentUser = null;
    
    public function setUser(User $user): void
    {
        $this->currentUser = $user;
    }
    
    public function processOrder(array $items): void
    {
        $total = $this->calculateTotal($items);
        $this->paymentGateway->charge($this->currentUser, $total);
    }
}

// AFTER: Stateless
class OrderProcessor
{
    public function processOrder(User $user, array $items): void
    {
        $total = $this->calculateTotal($items);
        $this->paymentGateway->charge($user, $total);
    }
}
```

### Step 5: Handle the setter caller
Find all places that called the removed setter. Pass the data directly to the method instead.

```php
// BEFORE
$processor->setUser($currentUser);
$processor->processOrder($items);

// AFTER
$processor->processOrder($currentUser, $items);
```

### Step 6: Evaluate ResetInterface
If the class implemented `ResetInterface`, assess whether to remove it:

- **If you successfully removed all ephemeral state** → Remove `ResetInterface` and `reset()`. The service is now truly stateless.
- **If ephemeral state remains because full statelessness is impractical** → Keep `ResetInterface`. Document which properties are request-scoped and ensure `reset()` clears all of them. Verify `reset()` is called reliably in all execution contexts (PHP-FPM, queue workers, long-running servers). This is a valid Symfony pattern and an acceptable solution when the refactor scope is too large.
- **If the service runs in a long-running or async context** → `ResetInterface` still works if you guarantee `reset()` is called between every request/message (e.g., via a custom kernel or worker loop). If you cannot guarantee this, then refactor to stateless.

### Step 7: Handle complex cases with DTOs
When a method needs many pieces of ephemeral state, group them into a DTO:

```php
class ProcessingContext  // DTO for grouped ephemeral state
{
    public function __construct(
        public readonly User $user,
        public readonly DateTime $processedAt,
        public readonly string $correlationId,
    ) {}
}

class OrderProcessor
{
    public function processOrder(ProcessingContext $context, array $items): void
    {
        // Use $context->user, $context->processedAt, etc.
    }
}
```

### Step 8: Handle listener/middleware patterns
For event listeners or middleware that need to pass context to downstream services, use stamps, attributes, or context bags instead of service state:

```php
// BEFORE: Listener stores state in service
class AuditListener
{
    private ?AdminUser $adminUser = null;
    
    public function onKernelRequest(RequestEvent $event): void
    {
        $this->adminUser = $event->getRequest()->attributes->get('adminUser');
    }
    
    public function onEntityChange(): void
    {
        $this->logger->log('Change by ' . $this->adminUser?->getUsername());
    }
}

// AFTER: Pass context explicitly
class AuditListener
{
    public function onEntityChange(EntityChangeEvent $event): void
    {
        $adminUser = $event->getContext()->getAdminUser();
        $this->logger->log('Change by ' . $adminUser?->getUsername());
    }
}
```

## RED / GREEN TDD workflow for stateful service bugs

Before refactoring a stateful service, write a failing test that proves the state leakage bug. Then make it pass with the stateless refactor.

### Step RED: Write a failing test that demonstrates state leakage

Create a test that calls the same service instance twice with different inputs and asserts the second call is not contaminated by the first.

```php
public function test_state_leaks_between_calls(): void
{
    $processor = new OrderProcessor($this->paymentGateway);
    $userA = new User('Alice');
    $userB = new User('Bob');

    // First call sets state for Alice
    $processor->setUser($userA);
    $processor->processOrder([new Item('book', 10)]);

    // Second call does NOT reset state — but we expect Bob
    // This test will FAIL because the service still holds Alice
    $processor->setUser($userB);
    $processor->processOrder([new Item('pen', 2)]);

    // Assert the payment gateway was called with Bob, not Alice
    $this->paymentGateway->assertChargedUser('Bob');
}
```

Run the test. It must fail. If it passes, the test does not actually reproduce the bug — fix the test.

### Step GREEN: Refactor to stateless and watch the test pass

Apply the refactoring strategy below to remove the ephemeral state. The same test should now pass without modification.

```php
public function test_state_leaks_between_calls(): void
{
    $processor = new OrderProcessor($this->paymentGateway);
    $userA = new User('Alice');
    $userB = new User('Bob');

    // Stateless: user passed as parameter, no internal state to leak
    $processor->processOrder($userA, [new Item('book', 10)]);
    $processor->processOrder($userB, [new Item('pen', 2)]);

    $this->paymentGateway->assertChargedUser('Bob');
}
```

### Step REFACTOR: Add comprehensive stateless tests

Once green, add tests that exercise the stateless service in parallel or looped contexts that would have been impossible before:

```php
public function test_parallel_calls_do_not_interfere(): void
{
    $processor = new OrderProcessor($this->paymentGateway);

    // Simulate multiple requests sharing the same service instance
    $processor->processOrder(new User('Alice'), [new Item('A', 1)]);
    $processor->processOrder(new User('Bob'), [new Item('B', 2)]);
    $processor->processOrder(new User('Charlie'), [new Item('C', 3)]);

    $this->paymentGateway->assertChargeCount(3);
    $this->paymentGateway->assertAllUsersChargedOnce(['Alice', 'Bob', 'Charlie']);
}
```

### Rules for RED / GREEN stateful service tests

1. The RED test must fail on the original stateful code. If it passes, it does not prove the bug.
2. The same test must pass after refactoring without changing the test logic.
3. Never skip the RED step. The failing test is the safety net that proves the bug existed.
4. If the service implements `ResetInterface`, include a test that calls the service without calling `reset()` between uses — this demonstrates the risk in contexts (queue workers, long-running servers) where `reset()` may not be called reliably.
5. After GREEN, add at least one test that exercises the service with interleaved or repeated calls to prove statelessness.

## Workflow when applying this skill

1. **Scan**: Search the codebase for the detection patterns above. Focus on `Infrastructure/`, `Client/`, services, listeners, middleware, and processors.
2. **Classify**: For each finding, classify the state type:
   - Configuration → Leave as-is
   - Dependencies → Leave as-is
   - Ephemeral → Mark for refactoring
3. **Prioritize**: Start with classes implementing `ResetInterface` (clear signal of request-scoped state), then setter-based state, then hidden parameter passing.
4. **Write RED test**: Before touching the service code, write a failing test that proves state leakage between calls.
5. **Refactor**: Apply the refactoring strategy above, one service at a time.
6. **Watch test go GREEN**: Run the same test. It should now pass.
7. **Add statelessness tests**: Add tests for parallel, looped, or interleaved usage that would have been unsafe before.
8. **Update callers**: Find and update all code that called removed setters or relied on the service state.
9. **Review**: Check that the refactored service no longer has detection patterns.

## Output format

When reporting findings, use this structure:

```markdown
## Stateful Service: ClassName

**File**: `path/to/ClassName.php`
**Pattern**: ResetInterface | Setter | HiddenParameter | Accumulation
**State held**: Description of the ephemeral state
**Risk**: Why this is problematic in the current or future architecture
**Refactor approach**: Brief description of how to make it stateless
**Estimated effort**: Small | Medium | Large
```

## Common edge cases

### Symfony Translator pattern
Symfony's translator itself has `setLocale()` — this is a framework-level stateful service. Your adapter wrapping it should NOT add more state. Pass locale as parameter to your adapter methods instead.

### Monolog processors
Monolog processors like `MessengerCorrelationIdProcessor` often use setters to receive context. Consider passing the correlation ID via LogRecord extras or using a processor that reads from a context DTO instead.

### Batch processing with accumulated errors
Instead of `$this->errors[]`, return result objects:
```php
class ProcessingResult
{
    public function __construct(
        public readonly bool $success,
        public readonly array $errors = [],
    ) {}
}
```

### RequestStack as dependency
Using `RequestStack` as a constructor dependency is generally fine (it's a dependency, not state), but calling `getCurrentRequest()` and storing the result in a property is stateful. Call it where needed, or pass the request object as a parameter.

## Remember

A service handling a single request today might become part of a queue worker or async process tomorrow. Stateless design future-proofs your code and makes it predictable, testable, and safe for any execution context.
