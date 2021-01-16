import useOnChange from "./useOnChange";
import { useEffect } from "react";
import Dataset from "../types/resource/dataset";
import useIncrement from "./useIncrement";
import { Resource } from "../types/resource";

type UseFormOptions<T extends Resource> = {
  service:
    T extends Dataset ? 'dataset' :
    'error',
  initial?: Partial<T>
}

function useForm<T extends Resource>({ initial, service }: UseFormOptions<T>) {
  const { data, onChange } = useOnChange<T>(initial);
  const { count, increment } = useIncrement();
  useEffect(() => {
    if (count) {
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
  }, [count]);
  return { create: increment, onChange };
}

export default useForm;
