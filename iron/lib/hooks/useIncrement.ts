import { useState } from 'react';

function useIncrement(initial: number = 0) {
    const [count, setCount] = useState<number>(initial);
    const increment = () => setCount(prev => prev + 1);
    return { count, increment };
}

export default useIncrement;
