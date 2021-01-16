import { Button, FormControl, Input, InputLabel } from "@material-ui/core";
import useForm from "../../lib/hooks/useForm";
import Dataset from '../../lib/types/resource/dataset';

export default function NewDataset() {
  const { create, onChange } = useForm<Dataset>({ service: "dataset", initial: {} });
  return (
    <form noValidate autoComplete="off">
      <FormControl fullWidth>
        <InputLabel htmlFor="dataset-name">Name</InputLabel>
        <Input id="dataset-name" onChange={onChange("name")} />
      </FormControl>
      <FormControl fullWidth>
        <InputLabel htmlFor="dataset-path">Path</InputLabel>
        <Input id="dataset-path" onChange={onChange("path")} />
      </FormControl>
      <Button variant="contained" color="primary" onClick={create}>
        Create
      </Button>
    </form>
  );
}
