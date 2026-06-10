import { CustomerLayout } from "../components/CustomerLayout";
import { useJourneyContext } from "../context/JourneyProvider";
import { CustomerScreens } from "../screens/CustomerScreens";

export function CustomerPage() {
  const store = useJourneyContext();
  return (
    <CustomerLayout>
      <CustomerScreens store={store} />
    </CustomerLayout>
  );
}
