import { useState } from 'react';

function useOnChange(initial = {}) {
  const [data, setValue] = useState(initial);

  const onChange = (name) => (e) =>
    setValue((prev) => ({ ...prev, [name]: e.target.value }));

  return { data, onChange };
}

export default useOnChange;
