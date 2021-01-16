import useOnChange from "./useOnChange";
import { useState, useEffect } from "react";
import Dataset from "../types/resource/dataset";

type UseFormOptions<T> = {
  service:
    T extends Dataset ? 'dataset' :
    'error',
  initial?: Partial<T>
}

function useForm<T>({ initial, service }: UseFormOptions<T>) {
  const { data, onChange } = useOnChange<T>(initial);
  const [id, setId] = useState(0);
  const create = () => setId((prev) => prev + 1);
  useEffect(() => {
    if (id) {
      (async () => {
        const res = await fetch(`/rest/${service}`, {
          method: "POST",
          body: JSON.stringify(data),
          headers: {
            "content-type": "application/json",
          },
        });
      })();
    }
  }, [id]);
  return { create, onChange };
}

export default useForm;
