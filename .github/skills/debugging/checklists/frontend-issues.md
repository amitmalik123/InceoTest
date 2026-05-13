# Frontend Issues

Investigation checklist for React, TypeScript, and JavaScript errors.

## Symptoms

- React hooks errors (invalid hook call, rules of hooks)
- Component not re-rendering
- TypeScript compilation errors
- State not updating as expected
- Infinite loops / Maximum update depth
- Memory leaks from subscriptions
- Build failures

## Quick Checks

1. **Is it a hooks issue?**
   - Hooks called conditionally?
   - Hooks called in wrong order?
   - Hooks outside functional component?

2. **Is it a state issue?**
   - Mutating state directly?
   - Stale closure over state?
   - Missing dependency in useEffect?

3. **Is it a TypeScript issue?**
   - Type mismatch?
   - Missing type definitions?
   - Strict mode violations?

4. **Is it a build issue?**
   - Node modules need reinstall?
   - Version conflicts?
   - Cache stale?

## Root Cause Patterns

| Error | Cause | Fix |
|-------|-------|-----|
| Invalid hook call | Hook in conditional/loop | Move to top level |
| Component not updating | Direct state mutation | Use setState with new object |
| Infinite loop in useEffect | Missing/wrong dependencies | Fix dependency array |
| Type error on props | Wrong prop type | Fix interface/type definition |
| Memory leak warning | Uncleared subscription | Return cleanup function |
| Build OOM | Large bundle / many deps | Increase memory, check imports |

## React Hooks Issues

### Rules of Hooks Violations

```tsx
// 🔴 Hook inside condition
function Component({ isEnabled }) {
  if (isEnabled) {
    const [state, setState] = useState(0);  // Error!
  }
}

// ✅ Hook at top level, use conditionally
function Component({ isEnabled }) {
  const [state, setState] = useState(0);

  if (!isEnabled) return null;
  return <div>{state}</div>;
}
```

### Stale Closure

```tsx
// 🔴 Stale closure over count
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCount(count + 1);  // Always uses initial count (0)
    }, 1000);
    return () => clearInterval(interval);
  }, []);  // Empty deps - closure captures initial count
}

// ✅ Use functional update
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCount(c => c + 1);  // Uses latest value
    }, 1000);
    return () => clearInterval(interval);
  }, []);
}
```

### Missing useEffect Dependencies

```tsx
// 🔴 Missing dependency causes stale data
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, []);  // Missing userId dependency!
}

// ✅ Include all dependencies
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, [userId]);  // Re-fetches when userId changes
}
```

### Infinite useEffect Loop

```tsx
// 🔴 Object/array created each render triggers infinite loop
function Component() {
  const [data, setData] = useState([]);
  const options = { page: 1 };  // New object each render

  useEffect(() => {
    fetch(url, options).then(setData);
  }, [options]);  // options changes every render!
}

// ✅ Use useMemo for objects/arrays in dependencies
function Component() {
  const [data, setData] = useState([]);
  const options = useMemo(() => ({ page: 1 }), []);

  useEffect(() => {
    fetch(url, options).then(setData);
  }, [options]);
}
```

## State Update Issues

### Direct State Mutation

```tsx
// 🔴 Mutating state directly - won't trigger re-render
function TodoList() {
  const [todos, setTodos] = useState([{ id: 1, text: 'Test' }]);

  const updateTodo = (id, text) => {
    const todo = todos.find(t => t.id === id);
    todo.text = text;  // Mutation!
    setTodos(todos);   // Same reference, no re-render
  };
}

// ✅ Create new objects/arrays
function TodoList() {
  const [todos, setTodos] = useState([{ id: 1, text: 'Test' }]);

  const updateTodo = (id, text) => {
    setTodos(todos.map(todo =>
      todo.id === id ? { ...todo, text } : todo
    ));
  };
}
```

### State Not Batched (React 17)

```tsx
// In React 17, state updates in async code aren't batched
// 🔴 Two re-renders
async function handleClick() {
  const data = await fetchData();
  setLoading(false);  // Re-render 1
  setData(data);      // Re-render 2
}

// ✅ Batch with unstable_batchedUpdates (React 17)
import { unstable_batchedUpdates } from 'react-dom';

async function handleClick() {
  const data = await fetchData();
  unstable_batchedUpdates(() => {
    setLoading(false);
    setData(data);
  });
}

// In React 18+, all updates are automatically batched
```

## TypeScript Issues

### Type Inference Failures

```tsx
// 🔴 TypeScript can't infer event type
const handleChange = (e) => {  // 'e' implicitly has 'any' type
  setValue(e.target.value);
};

// ✅ Explicitly type the event
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  setValue(e.target.value);
};
```

### Generic Component Props

```tsx
// 🔴 Loss of type information
interface ListProps {
  items: any[];
  renderItem: (item: any) => React.ReactNode;
}

// ✅ Use generics
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}

function List<T>({ items, renderItem }: ListProps<T>) {
  return <>{items.map(renderItem)}</>;
}
```

### Discriminated Unions for State

```tsx
// 🔴 State can be in impossible states
interface State {
  isLoading: boolean;
  error: string | null;
  data: Data | null;
}

// ✅ Use discriminated unions
type State =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'error'; error: string }
  | { status: 'success'; data: Data };
```

## Memory Leaks

### Uncleared Subscriptions

```tsx
// 🔴 Memory leak - no cleanup
function Component() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const subscription = dataSource.subscribe(setData);
    // Missing cleanup!
  }, []);
}

// ✅ Return cleanup function
function Component() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const subscription = dataSource.subscribe(setData);
    return () => subscription.unsubscribe();
  }, []);
}
```

### State Update After Unmount

```tsx
// 🔴 Can't update state on unmounted component
function Component() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchData().then(setData);  // Component might unmount before this resolves
  }, []);
}

// ✅ Use AbortController or flag
function Component() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const controller = new AbortController();

    fetchData({ signal: controller.signal })
      .then(setData)
      .catch(e => {
        if (e.name !== 'AbortError') throw e;
      });

    return () => controller.abort();
  }, []);
}
```

## Build and Module Issues

### Node Modules Problems

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Or with npm cache clear
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### TypeScript Declaration Errors

```bash
# Missing type definitions
npm install --save-dev @types/react @types/react-dom

# Check for type version mismatches
npm ls @types/react
```

### Vite/Webpack Build Issues

```bash
# Clear build cache
rm -rf dist .vite node_modules/.vite

# Vite with increased memory
NODE_OPTIONS="--max-old-space-size=4096" npm run build
```

## Debugging Steps

1. **Check React DevTools:**
   - Component tree structure
   - Props and state values
   - Hook inspection

2. **Add React StrictMode:**
   ```tsx
   // Catches issues by double-invoking functions
   <React.StrictMode>
     <App />
   </React.StrictMode>
   ```

3. **Enable TypeScript strict mode:**
   ```json
   // tsconfig.json
   {
     "compilerOptions": {
       "strict": true,
       "noImplicitAny": true,
       "strictNullChecks": true
     }
   }
   ```

4. **Profile renders:**
   ```tsx
   // React DevTools Profiler
   // Or use why-did-you-render
   import whyDidYouRender from '@welldone-software/why-did-you-render';
   whyDidYouRender(React);
   ```

5. **Check for console errors/warnings:**
   - React warnings about keys
   - Prop type warnings
   - Hook order warnings

## Prevention

- Use ESLint with `eslint-plugin-react-hooks`
- Enable TypeScript strict mode
- Write tests with React Testing Library
- Use React.StrictMode in development
- Keep components small and focused
- Memoize expensive computations with useMemo
- Use React.memo for expensive components
- Handle loading and error states explicitly
