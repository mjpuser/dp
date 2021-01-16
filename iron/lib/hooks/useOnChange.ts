import { useState } from 'react';

function useOnChange<T>(initial: Partial<T>) {
  const [data, setValue] = useState<Partial<T>>(initial ?? {});

  const onChange = (name: keyof T) => (e: any) =>
    setValue((prev) => ({ ...prev, [name]: e.target.value }));

  return { data, onChange };
}

export default useOnChange;
